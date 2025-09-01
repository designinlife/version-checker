from asyncio import Semaphore
from typing import List
import asyncio
import re

from loguru import logger

from app.core.config import GitLsRemoteSoftware
from app.core.version import VersionHelper
from . import Base


class Parser(Base):
    async def handle(self, sem: Semaphore, soft: GitLsRemoteSoftware):
        logger.debug(f'Name: {soft.name} ({soft.parser})')

        vhlp = VersionHelper(pattern=soft.pattern, split=soft.split, download_urls=soft.download_urls)

        async with sem:
            result = await self.run_command(['git', 'ls-remote', '--tags', soft.url])

            returncode = result['returncode']

            if returncode != 0:
                logger.error(f'Name: {soft.name}, Error: {result['stderr']}')
                return

            stdout = result['stdout']
            # vhlp.append(v['name'])
            for line in stdout.splitlines():
                v = self.parse_version(line)

                if v is not None:
                    vhlp.append(v)

            logger.debug(f'Name: {soft.name}, Versions: {vhlp.versions}, Summary: {vhlp.summary}')

            if soft.split > 0:
                logger.debug(f'Split Versions: {vhlp.split_versions}')

            # Write data to file.
            await self.write(soft, vhlp.summary)

    async def run_command(self, command):
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait for the subprocess to complete and get output
        stdout, stderr = await process.communicate()

        # Decode output and return results
        return {
            'returncode': process.returncode,
            'stdout': stdout.decode() if stdout else '',
            'stderr': stderr.decode() if stderr else ''
        }

    def parse_version(self, text: str):
        """
        Parse version number from a string like 'a310c093c61ceb6e1b8073cddf610c50c2fae6f3 refs/tags/v2.75'.
        Supports formats like 'vX.Y' or 'vX.Y.Z'.
        Returns the version string (e.g., 'v2.75' or 'v2.75.0') or None if not found.
        """
        # Regular expression to match version numbers (vX.Y or vX.Y.Z)
        pattern = r'refs/tags/(v?\d+\.\d+(?:\.\d+)?)$'
        match = re.search(pattern, text)
        return match.group(1) if match else None
