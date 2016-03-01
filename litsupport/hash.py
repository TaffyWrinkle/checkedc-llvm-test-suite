from lit.Test import toMetricValue
import hashlib
import logging
import subprocess
import shutil
import platform
import shellcommand


def compute(context):
    executable = context.executable
    try:
        # Darwin's "strip" doesn't support these arguments.
        if platform.system() != 'Darwin':
            stripped_executable = executable + '.stripped'
            shutil.copyfile(executable, stripped_executable)
            subprocess.check_call(['strip',
                                   '--remove-section=.comment',
                                   '--remove-section=.note',
                                   stripped_executable])
            executable = stripped_executable

        h = hashlib.md5()
        h.update(open(executable, 'rb').read())
        context.executable_hash = h.hexdigest()
    except:
        logging.info('Could not calculate hash for %s' % executable)
        context.executable_hash = None


def same_as_previous(context):
    """Check whether hash has changed compared to the results in
    config.previous_results."""
    previous_results = context.config.previous_results
    testname = context.test.getFullName()
    executable_hash = context.executable_hash
    if previous_results and "tests" in previous_results:
        for test in previous_results["tests"]:
            if "name" not in test or test["name"] != testname:
                continue
            if "metrics" not in test:
                continue
            metrics = test["metrics"]
            return "hash" in metrics and metrics["hash"] == executable_hash
    return False


def collect(context, result):
    if context.executable_hash is not None:
        result.addMetric('hash', toMetricValue(context.executable_hash))
