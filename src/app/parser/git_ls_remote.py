import asyncio
import re
from asyncio import Semaphore

from loguru import logger

from app.core.config import GitLsRemoteSoftware
from app.core.version import VersionHelper

from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: GitLsRemoteSoftware):
        """执行 `git ls-remote --tags` 获取远端标签，并从输出行中提取版本号。"""
        logger.debug(f"Name: {soft.name} ({soft.parser})")

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            result = await self.run_command(["git", "ls-remote", "--tags", soft.url])

            returncode = result["returncode"]

            if returncode != 0:
                logger.error(f"Name: {soft.name}, Error: {result['stderr']}")
                return

            stdout = result["stdout"]
            for line in stdout.splitlines():
                v = self.parse_version(line)

                if v is not None:
                    vhlp.append(v)

            logger.debug(f"Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}")

            if soft.split > 0:
                logger.debug(f"Split Versions: {vhlp.split_versions}")

            await self.write(soft, vhlp.summary)

    async def run_command(self, command):
        """异步执行外部命令并返回退出码、标准输出和标准错误。"""
        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await process.communicate()

        return {"returncode": process.returncode, "stdout": stdout.decode() if stdout else "", "stderr": stderr.decode() if stderr else ""}

    def parse_version(self, text: str):
        """从 `git ls-remote` 输出行中提取 `vX.Y` 或 `vX.Y.Z` 形式的标签。"""
        pattern = r"refs/tags/(v?\d+\.\d+(?:\.\d+)?)$"
        match = re.search(pattern, text)
        return match.group(1) if match else None
