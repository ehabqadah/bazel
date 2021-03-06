# Copyright 2018 The Bazel Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest

from src.test.py.bazel import test_base


class TestWrapperTest(test_base.TestBase):

  @staticmethod
  def _ReadFile(path):
    # Read the runfiles manifest.
    contents = []
    with open(path, 'rt') as f:
      contents = [line.strip() for line in f.readlines()]
    return contents

  def _FailWithOutput(self, output):
    self.fail('FAIL:\n | %s\n---' % '\n | '.join(output))

  def _CreateMockWorkspace(self):
    self.ScratchFile('WORKSPACE')
    # All test targets are called <something>.bat, for the benefit of Windows.
    # This makes test execution faster on Windows for the following reason:
    #
    # When building a sh_test rule, the main output's name is the same as the
    # rule. On Unixes, this output is a symlink to the main script (the first
    # entry in `srcs`), on Windows it's a copy of the file. In fact the main
    # "script" does not have to be a script, it may be any executable file.
    #
    # On Unixes anything with the +x permission can be executed; the file's
    # shebang line specifies the interpreter. On Windows, there's no such
    # mechanism; Bazel runs the main script (which is typically a ".sh" file)
    # through Bash. However, if the main file is a native executable, it's
    # faster to run it directly than through Bash (plus it removes the need for
    # Bash).
    #
    # Therefore on Windows, if the main script is a native executable (such as a
    # ".bat" file) and has the same extension as the main file, Bazel (in case
    # of sh_test) makes a copy of the file and runs it directly, rather than
    # through Bash.
    self.ScratchFile('foo/BUILD', [
        'sh_test(',
        '    name = "passing_test.bat",',
        '    srcs = ["passing.bat"],',
        ')',
        'sh_test(',
        '    name = "failing_test.bat",',
        '    srcs = ["failing.bat"],',
        ')',
        'sh_test(',
        '    name = "printing_test.bat",',
        '    srcs = ["printing.bat"],',
        ')',
        'sh_test(',
        '    name = "runfiles_test.bat",',
        '    srcs = ["runfiles.bat"],',
        '    data = ["passing.bat"],',
        ')',
        'sh_test(',
        '    name = "sharded_test.bat",',
        '    srcs = ["sharded.bat"],',
        '    shard_count = 2,',
        ')',
        'sh_test(',
        '    name = "unexported_test.bat",',
        '    srcs = ["unexported.bat"],',
        ')',
        'sh_test(',
        '    name = "testargs_test.bat",',
        '    srcs = ["testargs.bat"],',
        '    args = ["foo", "a b", "", "bar"],',
        ')',
    ])
    self.ScratchFile('foo/passing.bat', ['@exit /B 0'], executable=True)
    self.ScratchFile('foo/failing.bat', ['@exit /B 1'], executable=True)
    self.ScratchFile(
        'foo/printing.bat', [
            '@echo lorem ipsum',
            '@echo HOME=%HOME%',
            '@echo TEST_SRCDIR=%TEST_SRCDIR%',
            '@echo TEST_TMPDIR=%TEST_TMPDIR%',
            '@echo USER=%USER%',
        ],
        executable=True)
    self.ScratchFile(
        'foo/runfiles.bat', [
            '@echo MF=%RUNFILES_MANIFEST_FILE%',
            '@echo ONLY=%RUNFILES_MANIFEST_ONLY%',
            '@echo DIR=%RUNFILES_DIR%',
        ],
        executable=True)
    self.ScratchFile(
        'foo/sharded.bat', [
            '@echo STATUS=%TEST_SHARD_STATUS_FILE%',
            '@echo INDEX=%TEST_SHARD_INDEX% TOTAL=%TEST_TOTAL_SHARDS%',
        ],
        executable=True)
    self.ScratchFile(
        'foo/unexported.bat', [
            '@echo GOOD=%HOME%',
            '@echo BAD=%TEST_UNDECLARED_OUTPUTS_MANIFEST%',
        ],
        executable=True)
    self.ScratchFile(
        'foo/testargs.bat',
        [
            '@echo arg=(%~nx0)',  # basename of $0
            '@echo arg=(%1)',
            '@echo arg=(%2)',
            '@echo arg=(%3)',
            '@echo arg=(%4)',
            '@echo arg=(%5)',
            '@echo arg=(%6)',
            '@echo arg=(%7)',
            '@echo arg=(%8)',
            '@echo arg=(%9)',
        ],
        executable=True)

  def _AssertPassingTest(self, flag):
    exit_code, _, stderr = self.RunBazel([
        'test',
        '//foo:passing_test.bat',
        '-t-',
        flag,
    ])
    self.AssertExitCode(exit_code, 0, stderr)

  def _AssertFailingTest(self, flag):
    exit_code, _, stderr = self.RunBazel([
        'test',
        '//foo:failing_test.bat',
        '-t-',
        flag,
    ])
    self.AssertExitCode(exit_code, 3, stderr)

  def _AssertPrintingTest(self, flag):
    exit_code, stdout, stderr = self.RunBazel([
        'test',
        '//foo:printing_test.bat',
        '-t-',
        '--test_output=all',
        flag,
    ])
    self.AssertExitCode(exit_code, 0, stderr)
    lorem = False
    for line in stderr + stdout:
      if line.startswith('lorem ipsum'):
        lorem = True
      elif line.startswith('HOME='):
        home = line[len('HOME='):]
      elif line.startswith('TEST_SRCDIR='):
        srcdir = line[len('TEST_SRCDIR='):]
      elif line.startswith('TEST_TMPDIR='):
        tmpdir = line[len('TEST_TMPDIR='):]
      elif line.startswith('USER='):
        user = line[len('USER='):]
    if not lorem:
      self._FailWithOutput(stderr + stdout)
    if not home:
      self._FailWithOutput(stderr + stdout)
    if not os.path.isabs(home):
      self._FailWithOutput(stderr + stdout)
    if not os.path.isdir(srcdir):
      self._FailWithOutput(stderr + stdout)
    if not os.path.isfile(os.path.join(srcdir, 'MANIFEST')):
      self._FailWithOutput(stderr + stdout)
    if not os.path.isabs(srcdir):
      self._FailWithOutput(stderr + stdout)
    if not os.path.isdir(tmpdir):
      self._FailWithOutput(stderr + stdout)
    if not os.path.isabs(tmpdir):
      self._FailWithOutput(stderr + stdout)
    if not user:
      self._FailWithOutput(stderr + stdout)

  def _AssertRunfiles(self, flag):
    exit_code, stdout, stderr = self.RunBazel([
        'test',
        '//foo:runfiles_test.bat',
        '-t-',
        '--test_output=all',
        # Ensure Bazel does not create a runfiles tree.
        '--experimental_enable_runfiles=no',
        flag,
    ])
    self.AssertExitCode(exit_code, 0, stderr)
    mf = mf_only = rf_dir = None
    for line in stderr + stdout:
      if line.startswith('MF='):
        mf = line[len('MF='):]
      elif line.startswith('ONLY='):
        mf_only = line[len('ONLY='):]
      elif line.startswith('DIR='):
        rf_dir = line[len('DIR='):]

    if mf_only != '1':
      self._FailWithOutput(stderr + stdout)

    if not os.path.isfile(mf):
      self._FailWithOutput(stderr + stdout)
    mf_contents = TestWrapperTest._ReadFile(mf)
    # Assert that the data dependency is listed in the runfiles manifest.
    if not any(
        line.split(' ', 1)[0].endswith('foo/passing.bat')
        for line in mf_contents):
      self._FailWithOutput(mf_contents)

    if not os.path.isdir(rf_dir):
      self._FailWithOutput(stderr + stdout)

  def _AssertShardedTest(self, flag):
    exit_code, stdout, stderr = self.RunBazel([
        'test',
        '//foo:sharded_test.bat',
        '-t-',
        '--test_output=all',
        flag,
    ])
    self.AssertExitCode(exit_code, 0, stderr)
    status = None
    index_lines = []
    for line in stderr + stdout:
      if line.startswith('STATUS='):
        status = line[len('STATUS='):]
      elif line.startswith('INDEX='):
        index_lines.append(line)
    if not status:
      self._FailWithOutput(stderr + stdout)
    # Test test-setup.sh / test wrapper only ensure that the directory of the
    # shard status file exist, not that the file itself does too.
    if not os.path.isdir(os.path.dirname(status)):
      self._FailWithOutput(stderr + stdout)
    if sorted(index_lines) != ['INDEX=0 TOTAL=2', 'INDEX=1 TOTAL=2']:
      self._FailWithOutput(stderr + stdout)

  def _AssertUnexportsEnvvars(self, flag):
    exit_code, stdout, stderr = self.RunBazel([
        'test',
        '//foo:unexported_test.bat',
        '-t-',
        '--test_output=all',
        flag,
    ])
    self.AssertExitCode(exit_code, 0, stderr)
    good = bad = None
    for line in stderr + stdout:
      if line.startswith('GOOD='):
        good = line[len('GOOD='):]
      elif line.startswith('BAD='):
        bad = line[len('BAD='):]
    if not good or bad:
      self._FailWithOutput(stderr + stdout)

  def _AssertTestArgs(self, flag, expected):
    exit_code, bazel_bin, stderr = self.RunBazel(['info', 'bazel-bin'])
    self.AssertExitCode(exit_code, 0, stderr)
    bazel_bin = bazel_bin[0]

    exit_code, stdout, stderr = self.RunBazel([
        'test',
        '//foo:testargs_test.bat',
        '-t-',
        '--test_output=all',
        '--test_arg=baz',
        '--test_arg="x y"',
        '--test_arg=""',
        '--test_arg=qux',
        flag,
    ])
    self.AssertExitCode(exit_code, 0, stderr)

    actual = []
    for line in stderr + stdout:
      if line.startswith('arg='):
        actual.append(str(line[len('arg='):]))
    self.assertListEqual(expected, actual)

  def testTestExecutionWithTestSetupSh(self):
    self._CreateMockWorkspace()
    flag = '--nowindows_native_test_wrapper'
    self._AssertPassingTest(flag)
    self._AssertFailingTest(flag)
    self._AssertPrintingTest(flag)
    self._AssertRunfiles(flag)
    self._AssertShardedTest(flag)
    self._AssertUnexportsEnvvars(flag)
    self._AssertTestArgs(
        flag,
        [
            '(testargs_test.bat)',
            '(foo)',
            '(a)',
            '(b)',
            '(bar)',
            # Note: debugging shows that test-setup.sh receives more-or-less
            # good arguments (let's ignore issues #6276 and #6277 for now), but
            # mangles the last few.
            # I (laszlocsomor@) don't know the reason (as of 2018-10-01) but
            # since I'm planning to phase out test-setup.sh on Windows in favor
            # of the native test wrapper, I don't intend to debug this further.
            # The test is here merely to guard against unwanted future change of
            # behavior.
            '(baz)',
            '("\\"x)',
            '(y\\"")',
            '("\\\\\\")',
            '(qux")'
        ])

  def testTestExecutionWithTestWrapperExe(self):
    self._CreateMockWorkspace()
    # As of 2018-09-11, the Windows native test runner can run simple tests and
    # export a few envvars, though it does not completely set up the test's
    # environment yet.
    flag = '--windows_native_test_wrapper'
    self._AssertPassingTest(flag)
    self._AssertFailingTest(flag)
    self._AssertPrintingTest(flag)
    self._AssertRunfiles(flag)
    self._AssertShardedTest(flag)
    self._AssertUnexportsEnvvars(flag)
    self._AssertTestArgs(
        flag,
        [
            '(testargs_test.bat)',
            '(foo)',
            # TODO(laszlocsomor): assert that "a b" is passed as one argument,
            # not two, after https://github.com/bazelbuild/bazel/issues/6277
            # is fixed.
            '(a)',
            '(b)',
            # TODO(laszlocsomor): assert that the empty string argument is
            # passed, after https://github.com/bazelbuild/bazel/issues/6276
            # is fixed.
            '(bar)',
            '(baz)',
            '("x y")',
            '("")',
            '(qux)',
            '()'
        ])


if __name__ == '__main__':
  unittest.main()
