import os
from pytest import fixture
import tarfile
from zipfile import ZipFile
from spacekit.analyzer.explore import HstCalPlots, HstSvmPlots
from spacekit.analyzer.scan import SvmScanner, CalScanner, import_dataset

# try:
#     from pytest_astropy_header.display import (PYTEST_HEADER_MODULES,
#                                                TESTED_VERSIONS)
# except ImportError:
#     PYTEST_HEADER_MODULES = {}
#     TESTED_VERSIONS = {}
PYTEST_HEADER_MODULES = {}
TESTED_VERSIONS = {}

try:
    from spacekit import __version__ as version
except ImportError:
    version = "unknown"

# The following line treats all DeprecationWarnings as exceptions.
from astropy.tests.helper import enable_deprecations_as_exceptions

enable_deprecations_as_exceptions()

# Uncomment and customize the following lines to add/remove entries
# from the list of packages for which version numbers are displayed
# when running the tests.
# PYTEST_HEADER_MODULES['astropy'] = 'astropy'
# PYTEST_HEADER_MODULES.pop('Matplotlib')
# PYTEST_HEADER_MODULES.pop('Pandas')
# PYTEST_HEADER_MODULES.pop('h5py')

TESTED_VERSIONS["spacekit"] = version


class Config:
    def __init__(self, env):
        SUPPORTED_ENVS = ["svm", "cal"]
        self.env = env

        if env.lower() not in SUPPORTED_ENVS:
            raise Exception(
                f"{env} is not a supported environment (supported envs: {SUPPORTED_ENVS})"
            )

        self.data_path = {
            "svm": os.path.join(f"tests/data/{env}/data.zip"),
            "cal": os.path.join(f"tests/data/{env}/data.zip"),
        }[env]

        self.kwargs = {"svm": dict(index_col="index"), "cal": dict(index_col="ipst")}

        self.decoder = {
            "svm": {"det": {0: "hrc", 1: "ir", 2: "sbc", 3: "uvis", 4: "wfc"}},
            "cal": {"instr": {0: "acs", 1: "cos", 2: "stis", 3: "wfc3"}},
        }


def pytest_addoption(parser):
    parser.addoption("--env", action="store", help="Environment to run tests against")


@fixture(scope="session")
def env(request):
    return request.config.getoption("--env")


@fixture(scope="session")
def app_config(env):
    cfg = Config(env)
    return cfg


@fixture(scope="session")
def res_data_path(app_config, tmp_path_factory):
    basepath = tmp_path_factory.getbasetemp()
    data_file = app_config.data_path
    with ZipFile(data_file, "r") as z:
        z.extractall(basepath)
        dname = os.path.basename(data_file.split(".")[0])
        data_path = os.path.join(basepath, dname)
    return data_path


@fixture(scope="session")
def scanner(app_config, res_data_path):
    # basepath = tmp_path_factory.getbasetemp()
    # data_file = app_config.data_path
    # with ZipFile(data_file, "r") as z:
    #     z.extractall(basepath)
    #     dname = os.path.basename(data_file.split(".")[0])
    #     data_path = os.path.join(basepath, dname)
    if app_config.env == "svm":
        scanner = SvmScanner(perimeter=f"{res_data_path}/20??-*-*-*", primary=-1)
    elif app_config.env == "cal":
        scanner = CalScanner(perimeter=f"{res_data_path}/20??-*-*-*", primary=-1)
    scanner.exp = app_config.env
    return scanner


@fixture(scope="session")
def explorer(app_config, res_data_path):
    # fname = "tests/data/svm/train/training.csv"
    fname = res_data_path
    df = import_dataset(
        filename=fname, kwargs=app_config.kwargs, decoder=app_config.decoder
    )
    if app_config.env == "svm":
        hst = HstSvmPlots(df)
    elif app_config.env == "cal":
        hst = HstCalPlots(df)
    hst.env = app_config.env
    return hst


# SVM PREP
@fixture(scope="session")  # "ibl738.tgz"
def single_visit_path(tmp_path_factory):
    visit_path = os.path.abspath("tests/data/svm/prep/singlevisits.tgz")
    basepath = tmp_path_factory.getbasetemp()
    with tarfile.TarFile.open(visit_path) as tar:
        tar.extractall(basepath)
        dname = os.path.basename(visit_path.split(".")[0])
        visit_path = os.path.join(basepath, dname)
    return visit_path


@fixture(scope="function")
def img_outpath(tmp_path):
    return os.path.join(tmp_path, "img")


# SVM PREDICT
@fixture(scope="function")
def svm_unlabeled_dataset():
    return "tests/data/svm/predict/unlabeled.csv"


@fixture(scope="session", params=["img.tgz", "img_pred.npz"])
def svm_pred_img(request, tmp_path_factory):
    img_path = os.path.join("tests/data/svm/predict", request.param)
    if img_path.split(".")[-1] == "tgz":
        basepath = tmp_path_factory.getbasetemp()
        with tarfile.TarFile.open(img_path) as tar:
            tar.extractall(basepath)
            fname = os.path.basename(img_path.split(".")[0])
            img_path = os.path.join(basepath, fname)
    return img_path


# SVM TRAIN
@fixture(scope="function")  # session
def svm_labeled_dataset():
    return "tests/data/svm/train/training.csv"


@fixture(scope="session", params=["img.tgz", "img_data.npz"])
def svm_train_img(request, tmp_path_factory):
    img_path = os.path.join("tests/data/svm/train", request.param)
    if img_path.split(".")[-1] == "tgz":
        basepath = tmp_path_factory.getbasetemp()
        with tarfile.TarFile.open(img_path) as tar:
            tar.extractall(basepath)
            fname = os.path.basename(img_path.split(".")[0])
            img_path = os.path.join(basepath, fname)
    return img_path


@fixture(scope="function")
def svm_train_npz():
    return "tests/data/svm/train/img_data.npz"


# GENERATOR: DRAW
@fixture(params=["single_reg.csv"])
def draw_mosaic_fname(request):
    return os.path.join("tests/data/svm/prep", request.param)


@fixture(params=["*", "ibl*", ""])
def draw_mosaic_pattern(request):
    return request.param


# PREPROCESSOR: SCRUB
@fixture(scope="function")
def raw_csv_file():
    return "tests/data/svm/prep/single_scrub.csv"


@fixture(scope="function")
def h5_data():
    return "tests/data/svm/prep/single_reg"


@fixture(scope="function")
def scrubbed_cols_file():
    return "tests/data/svm/prep/scrubbed_cols.csv"


@fixture(scope="function")
def scraped_fits_file():
    return "tests/data/svm/prep/scraped_fits.csv"


@fixture(scope="function")
def scraped_mast_file():
    return "tests/data/svm/prep/scraped_mast.csv"
