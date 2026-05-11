from typing import Awaitable, Callable, Optional
import asyncio
import contextlib

from aiopubsub.logging_compat import get_logger


class Loop:
	'''
	Run a coroutine in a loop with a delay after every iteration.
	The loop can be conveniently started, stopped, and restarted.
	'''

	def __init__(
		self,
		coro: Callable[[], Awaitable[None]],
		delay: Optional[float],
		name: Optional[str] = None,
	) -> None:
		self.coro = coro
		# pylint in Python 3.8 thinks that Future is unsubscriptable
		self.task: Optional[asyncio.Future[None]] = None  # pylint: disable=unsubscriptable-object
		self.delay = delay
		self.name: str
		if name is None:
			self.name = repr(coro)
			if hasattr(coro, '__name__'):
				self.name = f'[{coro.__name__}, {coro}]'
		else:
			self.name = name

		self._is_running = asyncio.Event()
		self._logger = get_logger(self.__class__.__name__)

	def start(self) -> None:
		if not self._is_running.is_set():
			self._is_running.set()
			asyncio.create_task(self._run(), name = self.name)

	def stop(self) -> None:
		self._is_running.clear()
		if self.task is not None:
			self.task.cancel()
			self.task = None

	async def stop_wait(self) -> None:
		self._is_running.clear()
		if self.task is not None:
			self.task.cancel()
			with contextlib.suppress(asyncio.CancelledError):
				await self.task
			self.task = None

	@property
	def is_running(self) -> bool:
		return self._is_running.is_set()

	async def _run(self) -> None:
		while self._is_running.is_set():
			self.task = asyncio.ensure_future(self.coro())
			try:
				await self.task
			except asyncio.CancelledError:
				if self._is_running.is_set():
					self._logger.exception('Unhandled CancelledError in = %s', self.name)
					raise
				self._logger.debug('Stopping task = %s', self.name)
				break
			except Exception:  # pylint: disable=broad-except
				self._logger.exception('Uncaught exception in _run in coroutine = %s', self.name)
				self._is_running.clear()
				raise
			if self.delay is not None:
				await asyncio.sleep(self.delay)
