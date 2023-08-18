"""
This module is a convenient and efficient tool for loading results metrics 
of multiple model training iterations into a single MegaScanner object. 
Metrics files can be loaded from disk and plotted for comparative model analysis 
and evaluation. Using this approach assumes model training results files match 
those generated by spacekit.analyzer.compute.Computer class/subclass objects 
and are accessible from the local disk. Primarily used by spacekit.dashboard 
but can easily be repurposed for other use-cases (analyzing model performance 
in Jupyter notebooks/Google Colab, for example).
"""
import os
import pandas as pd
import glob
from spacekit.analyzer.compute import ComputeBinary, ComputeMulti, ComputeRegressor
from spacekit.logger.log import Logger
from spacekit.skopes.jwst.cal.config import KEYPAIR_DATA

try:
    import plotly.graph_objects as go
    import plotly.figure_factory as ff
    from plotly import subplots
except ImportError:
    go = None
    ff = None
    subplots = None


def check_plotly():
    return go is not None


def decode_categorical(df, decoder_key):
    """Add decoded column (using "{column}_key" suffix) to dataframe.

    Parameters
    ----------
    df : pandas DataFrame
        dataframe with encoded categorical column
    decoder_key : dict
        key-value pairs of encoding integers and strings

    Returns
    -------
    pandas DataFrane
        dataframe with additional categorical column (object dtype) decoded
        back to strings based on encoding pairs passed in decoder_key.
    """
    for key, pairs in decoder_key.items():
        for i, name in pairs.items():
            df.loc[df[key] == i, f"{key}_key"] = name
    return df


def import_dataset(filename=None, kwargs=dict(index_col="ipst"), decoder_key=None):
    """Imports and loads dataset from csv file. Optionally decodes an encoded feature back into strings.

    Parameters
    ----------
    filename : str, optional
        path to dataframe csv file, by default None
    kwargs : dict, optional
        keyword args to pass into pandas read_csv method, by default dict(index_col="ipst")
    decoder_key : dict, optional
        nested dict of column and key value pairs for decoding a categorical feature into strings., by default None

    Returns
    -------
    Pandas DataFrame
        dataframe loaded from csv file
    """
    if not os.path.exists(filename):
        print("File could not be found")
    # load dataset
    df = pd.read_csv(filename, **kwargs)
    if decoder_key:
        df = decode_categorical(df, decoder_key)  # adds instrument label (string)
    return df


class MegaScanner:
    """
    Scans local disk for Compute object datasets and results files then loads them
    as attributes for use in plotting, EDA, and model evaluation.

    Parameters
    ----------
    perimeter : str, optional
        glob search pattern
    primary : int, optional
        index of primary dataset to use for EDA in sorted list of those found, by default -1

    """

    def __init__(
        self, perimeter="data/20??-*-*-*", primary=-1, name="MegaScanner", **log_kws
    ):
        self.__name__ = name
        self.log = Logger(self.__name__, **log_kws).spacekit_logger()
        self.perimeter = perimeter
        self.datapaths = sorted(list(glob.glob(perimeter)))
        self.datasets = [d.split("/")[-1] for d in self.datapaths]
        self.timestamps = [
            int(t.split("-")[-1]) for t in self.datasets
        ]  # [1636048291, 1635457222, 1629663047]
        self.dates = [
            str(v)[:10] for v in self.datasets
        ]  # ["2021-11-04", "2021-10-28", "2021-08-22"]
        self.primary = primary
        self.data = None  # self.select_dataset()
        self.versions = None
        self.res_keys = None
        self.target = None
        self.labels = None
        self.classes = None
        self.mega = None  # self.make_mega()
        self.kwargs = None
        self.decoder = None
        self.df = None  # self.load_dataframe()
        self.scores = None  # self.compare_scores()
        self.acc_fig = None  # self.accuracy_bars()
        self.loss_fig = None  # self.loss_bars()
        self.acc_loss_figs = None  # self.acc_loss_subplots()
        self.res_fig = None  # TODO
        self.keras = {}
        self.roc = {}
        self.cmx = {}
        if not check_plotly():
            self.log.error("plotly not installed.")
            raise ImportError(
                "You must install plotly (`pip install plotly`) "
                "for the scan module to work."
                "\n\nInstall extra deps via `pip install spacekit[x]`"
            )

    def select_dataset(self, primary=None):
        """Select which dataset file (if there are multiple timestamps) to use, e.g. for performing EDA.

        Parameters
        ----------
        primary : int, optional
            index of primary dataset to use in sorted list of those found, by default None (-1 or most recent timestamp)

        Returns
        -------
        str
            path to csv file of saved dataframe according to the primary index key of datasets found.

        Raises
        ------
        IndexError
            primary index key must be a value between zero and the last index of the list of datasets.
        """
        if primary:
            self.primary = primary
        if self.primary > len(self.datapaths):
            self.log.warning("Using default index (-1)")
            self.primary = -1
        if len(self.datapaths) > 0:
            dataset_path = self.datapaths[self.primary]
            self.data = glob.glob(f"{dataset_path}/data/*.csv")[0]
            return self.data
        else:
            return None

    def make_mega(self):
        """Instantiate an empty nested dictionary of results files for each timestamp.

        Returns
        -------
        dict
            self.mega nested dictionary for storing results
        """
        self.mega = {}
        versions = []
        for i, (d, t) in enumerate(zip(self.dates, self.timestamps)):
            if self.versions is None:
                v = f"v{str(i)}"
                versions.append(v)
            else:
                v = self.versions[i]
            self.mega[v] = {"date": d, "time": t, "res": self.res_keys}
        if len(versions) > 0:
            self.versions = versions
        return self.mega

    def load_compute_object(
        self, Com=ComputeMulti, alg="clf", res_path="results", validation=False
    ):
        """Loads a single compute object of any type with results from one iteration.

        Parameters
        ----------
        Com : spacekit.analyze.compute.Computer class, optional
            Compute subclass, by default ComputeMulti
        alg : str, optional
            algorithm type, by default "clf"
        res_path : str, optional
            path to results directory, by default "results"
        validation : bool, optional
            validation data results (no training history), by default False

        Returns
        -------
        spacekit.analyze.compute.Computer object
            Results from the given path loaded as attributes into a Compute class object
        """
        if alg in ["reg", "linreg"]:
            com = Com(algorithm=alg, res_path=res_path, validation=validation)
        else:
            com = Com(
                algorithm=alg,
                classes=self.labels,
                res_path=res_path,
                validation=validation,
            )
        out = com.upload()
        com.load_results(out)
        if alg == "clf":
            try:  # initialize Compute figure attrs
                com.draw_plots()
            except Exception as e:
                self.log.error(e)
        return com

    def _scan_results(self, coms=[ComputeBinary], algs=["clf"], names=["test"]):
        """Scans local disk for Computer object-generated results files of model training iterations.

        Returns
        -------
        MegaScanner.mega dictionary attribute
            dictionary of model training results for each iteration found.
        """
        objects = list(zip(coms, algs, names))
        self.mega = self.make_mega()
        for i, d in enumerate(self.datapaths):
            v = self.versions[i]
            for C, A, N in objects:
                com = C(algorithm=A, classes=self.labels, res_path=f"{d}/results/{N}")
                com_out = com.upload()
                com.load_results(com_out)
                self.mega[v]["res"][N] = com
        return self.mega

    def load_dataframe(self):
        self.df = import_dataset(
            filename=self.data, kwargs=self.kwargs, decoder_key=self.decoder
        )
        return self.df

    def make_clf_plots(self, target="mem_bin"):
        for v in self.versions:
            self.mega[v]["res"][target].draw_plots()
            self.keras[v] = [
                self.mega[v]["res"][target].acc_fig,
                self.mega[v]["res"][target].loss_fig,
            ]
            self.roc[v] = [
                self.mega[v]["res"][target].roc_fig,
                self.mega[v]["res"][target].pr_fig,
            ]
        # cmx for all versions displayed at once, unlike the two attrs above
        self.cmx = {
            "normalized": [self.mega[v]["res"][target].cmx_norm for v in self.versions],
            "counts": [self.mega[v]["res"][target].cmx for v in self.versions],
        }

    def make_barplots(self, metric="acc_loss"):
        self.compare_scores(metric=metric)
        self.acc_fig = self.accuracy_bars()
        self.loss_fig = self.loss_bars()
        self.acc_loss_subplots()

    def compare_scores(self, metric="acc_loss"):
        """Create a dictionary of model scores for multiple training iterations.
        Score type depends on the type of model: classifiers typically use "acc_loss";
        Regression models typically use "loss".

        Parameters
        ----------
        target : str, optional
            y target class label, by default "mem_bin"
        score_type : str, optional
            metric used by model (clf=acc_loss, reg=loss), by default "acc_loss"

        Returns
        -------
        Pandas dataframe
            model evaluation metrics scores (accuracy/loss by default) for each model training iteration
        """
        score_dfs = []
        for v in self.versions:
            if metric == "acc_loss":
                score_dict = self.mega[v]["res"][self.target].acc_loss
            else:
                score_dict = self.mega[v]["res"][self.target].loss
            df = pd.DataFrame.from_dict(score_dict, orient="index", columns=[v])
            score_dfs.append(df)
        self.scores = pd.concat([d for d in score_dfs], axis=1)
        return self.scores

    # TODO: this can be combined with loss_bars, use kwargs to distinguish between metrics
    def accuracy_bars(self):
        """Barplots of training and test set accuracy scores loaded from a Pandas dataframe

        Returns
        -------
        plotly.graph_objs.Figure
            Grouped barplot figure data of training and test set accuracy scores.
        """
        acc_train = self.scores.loc["train_acc"].values
        acc_test = self.scores.loc["test_acc"].values
        xvals = [c for c in self.scores.columns]
        data = [
            go.Bar(
                x=list(range(len(acc_train))),
                hovertext=xvals,
                y=acc_train,
                name="Training Accuracy",
                marker=dict(color="dodgerblue"),
            ),
            go.Bar(
                x=list(range(len(acc_test))),
                hovertext=xvals,
                y=acc_test,
                name="Test Accuracy",
                marker=dict(color="#66c2a5"),
            ),
        ]
        layout = go.Layout(
            title="Accuracy",
            xaxis={"title": "training iteration"},
            yaxis={"title": "score"},
            paper_bgcolor="#242a44",
            plot_bgcolor="#242a44",
            font={"color": "#ffffff"},
        )
        fig = go.Figure(data=data, layout=layout)
        return fig

    def loss_bars(self):
        """Barplots of training and test set loss scores loaded from a Pandas dataframe

        Returns
        -------
        plotly.graph_objs.Figure
            Grouped barplot figure data of training and test set loss scores.
        """
        loss_train = self.scores.loc["train_loss"].values
        loss_test = self.scores.loc["test_loss"].values
        xvals = [c for c in self.scores.columns]
        data = [
            go.Bar(
                x=list(range(len(loss_train))),
                y=loss_train,
                hovertext=xvals,
                name="Training Loss",
                marker=dict(color="salmon"),
            ),
            go.Bar(
                x=list(range(len(loss_test))),
                y=loss_test,
                hovertext=xvals,
                name="Test Loss",
                marker=dict(color="peachpuff"),
            ),
        ]
        layout = go.Layout(
            title="Loss",
            xaxis={"title": "training iteration"},
            yaxis={"title": "score"},
            paper_bgcolor="#242a44",
            plot_bgcolor="#242a44",
            font={"color": "#ffffff"},
        )
        fig = go.Figure(
            data=data,
            layout=layout,
        )
        return fig

    def acc_loss_subplots(self):
        """Side by side grouped barplots of accuracy and loss metrics for multiple model training iterations.

        Returns
        -------
        plotly.subplots object
            plot figure traces and layout for side by side Accuracy and Loss grouped barplots
        """
        self.acc_loss_fig = subplots.make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("Accuracy", "Loss"),
            shared_yaxes=False,
            x_title="Training Iteration",
            y_title="Score",
        )
        self.acc_loss_fig.add_trace(self.acc_fig.data[0], 1, 1)
        self.acc_loss_fig.add_trace(self.acc_fig.data[1], 1, 1)
        self.acc_loss_fig.add_trace(self.loss_fig.data[0], 1, 2)
        self.acc_loss_fig.add_trace(self.loss_fig.data[1], 1, 2)
        self.acc_loss_fig.update_layout(
            title_text="Accuracy vs. Loss",
            margin=dict(t=50, l=200),
            paper_bgcolor="#242a44",
            plot_bgcolor="#242a44",
            font={
                "color": "#ffffff",
            },
        )
        return self.acc_loss_fig

    def single_cmx(
        self, cmx, subtitles=("v0"), zmin=0.0, zmax=1.0, cmx_type="normalized"
    ):
        """Confusion matrix plot for a single model training iteration

        Parameters
        ----------
        cmx : 2D numpy array
            confusion matrix
        zmin : int or float
            typically 0 or 0.0 (minimum value for colorscale)
        zmax : int
            typically 1 (if normalized) or 100 (max value for colorscale)
        classes : list of strings
            target class labels
        subtitles : tuple, optional
            text to place above each plot as a subtitle, by default ("v0")

        Returns
        -------
        plotly figure factory annotated heatmap figure
            interactive confusion matrix plot
        """
        x = self.labels
        y = x[::-1].copy()
        z = cmx[::-1]
        if cmx_type == "normalized":
            zmin = 0.0
            zmax = 1.0
            fmt = "{:.2f}"
        else:
            zmin = 0
            zmax = 100
            fmt = "{:d}"
        z_text = [[fmt.format(y) for y in x] for x in z]
        subplot_titles = subtitles

        fig = subplots.make_subplots(
            rows=1,
            cols=1,
            subplot_titles=subplot_titles,
            shared_yaxes=False,
            x_title="Predicted",
            y_title="Actual",
        )
        fig.update_layout(
            title_text="Confusion Matrix",
            paper_bgcolor="#242a44",
            plot_bgcolor="#242a44",
            font={"color": "#ffffff"},
        )
        # make traces
        fig1 = ff.create_annotated_heatmap(
            z=z,
            x=x,
            y=y,
            annotation_text=z_text,
            colorscale="Blues",
            zmin=zmin,
            zmax=zmax,
        )
        fig.add_trace(fig1.data[0], 1, 1)
        annot1 = list(fig1.layout.annotations)
        annos = [annot1]

        # add colorbar
        fig["data"][0]["showscale"] = True
        # annotation values for each square
        for anno in annos:
            fig.add_annotation(anno)
        return fig

    def triple_cmx(self, cmx, cmx_type):
        """Plot three confusion matrices side by side

        Parameters
        ----------
        cmx_type : str
            "normalized" will return a normalized CMX (percentage of FNFPs), otherwise raw numeric values are displayed.

        Returns
        -------
        plotly figure factory annotated heatmap subplots
            three interactive confusion matrices side by side as a subplot
        """
        if cmx_type == "normalized":
            zmin = 0.0
            zmax = 1.0
            fmt = "{:.2f}"
        else:
            zmin = 0
            zmax = 100
            fmt = "{:d}"
        x = self.labels
        y = x[::-1].copy()
        subplot_titles = self.versions  # ("v1", "v2", "v3")
        fig = subplots.make_subplots(
            rows=1,
            cols=3,
            subplot_titles=subplot_titles,
            shared_yaxes=False,
            x_title="Predicted",
            y_title="Actual",
        )
        fig.update_layout(
            title_text="Confusion Matrix",
            paper_bgcolor="#242a44",
            plot_bgcolor="#242a44",
            font={"color": "#ffffff"},
        )
        annos = []
        for i in list(range(len(cmx))):
            col = i + 1
            z = cmx[i][::-1]
            z_text = [[fmt.format(y) for y in x] for x in z]
            cmx_fig = ff.create_annotated_heatmap(
                z=z,
                x=x,
                y=y,
                annotation_text=z_text,
                colorscale="Blues",
                zmin=zmin,
                zmax=zmax,
            )
            fig.add_trace(cmx_fig.data[0], 1, col)
            annot = list(cmx_fig.layout.annotations)

            for k in range(len(annot)):
                annot[k]["xref"] = f"x{str(col)}"
                annot[k]["yref"] = f"y{str(col)}"
            annos.append(annot)
        new_annotations = []
        for a in annos:
            new_annotations.extend(a)
        # add colorbar
        fig["data"][0]["showscale"] = True
        # annotation values for each square
        for anno in new_annotations:
            fig.add_annotation(anno)
        return fig


class HstCalScanner(MegaScanner):
    """MegaScanner subclass for HST calibration model training iteration analysis

    Parameters
    ----------
    MegaScanner : object
        Parent class object
    """

    def __init__(self, perimeter="data/20??-*-*-*", primary=-1, **log_kws):
        super().__init__(
            perimeter=perimeter, primary=primary, name="HstCalScanner", **log_kws
        )
        self.labels = ["2g", "8g", "16g", "64g"]
        self.classes = [0, 1, 2, 3]
        self.res_keys = dict(mem_bin=None, memory=None, wallclock=None)
        self.target = list(self.res_keys.keys())[0]
        self.data = self.select_dataset()
        self.mega = self.make_mega()
        self.kwargs = dict(index_col="ipst")
        self.decoder = {"instr": {0: "acs", 1: "cos", 2: "stis", 3: "wfc3"}}

    def scan_results(self):
        """Scans local disk for Computer object-generated results files and stores
        them as new Compute objects (according to the model type) in a nested dictionary.

        Returns
        -------
        HstCalScanner.mega dictionary attribute
            dictionary of model training results for each iteration found.
        """
        com_objects = []
        for d in self.datapaths:
            coms = self.load_com_objects(d)
            com_objects.append(coms)
            del coms

        for i in list(range(len(self.versions))):
            v = self.versions[i]
            b, m, w = com_objects[i]
            self.mega[v]["res"] = dict(mem_bin=b, memory=m, wallclock=w)
            del b, m, w
        return self.mega

    def load_com_objects(self, dpath):
        """Loads Multi classifier and Regression compute objects (3 total) for a single iteration of results

        Parameters
        ----------
        dpath : str
            dataset subdirectory path, e.g. "data/2022-02-03/results"

        Returns
        -------
        tuple
            tuple of mem_bin, memory, wallclock compute objects for one iteration
        """
        B = super().load_compute_object(
            Com=ComputeMulti, alg="clf", res_path=f"{dpath}/results/mem_bin"
        )
        M = super().load_compute_object(
            Com=ComputeRegressor, alg="linreg", res_path=f"{dpath}/results/memory"
        )
        W = super().load_compute_object(
            Com=ComputeRegressor, alg="linreg", res_path=f"{dpath}/results/wallclock"
        )
        return (B, M, W)


class HstSvmScanner(MegaScanner):
    """MegaScanner subclass for HST Single Visit Mosaic alignment model training iteration analysis

    Parameters
    ----------
    MegaScanner : parent class object
        MegaScanner object
    """

    def __init__(self, perimeter="data/20??-*-*-*", primary=-1, **log_kws):
        super().__init__(
            perimeter=perimeter, primary=primary, name="HstSvmScanner", **log_kws
        )
        self.labels = ["aligned", "misaligned"]
        self.classes = [0, 1]
        self.res_keys = {"test": {}, "val": {}}
        self.target = list(self.res_keys.keys())[0]
        self.data = self.select_dataset()
        self.mega = self.make_mega()
        self.kwargs = dict(index_col="index")
        self.decoder = {"det": {0: "hrc", 1: "ir", 2: "sbc", 3: "uvis", 4: "wfc"}}

    def scan_results(self):
        """Scans local disk for Computer object-generated results files and stores
        them as new Compute objects (according to the model type) in a nested dictionary.

        Returns
        -------
        HstSvmScanner.mega dictionary attribute
            dictionary of model training results for each iteration found.
        """
        com_objects = []
        for d in self.datapaths:
            coms = self.load_com_objects(d)
            com_objects.append(coms)
            del coms

        for i in list(range(len(self.versions))):
            v = self.versions[i]
            tcom, vcom = com_objects[i]
            self.mega[v]["res"] = dict(test=tcom, val=vcom)
            del tcom, vcom
        # return self.mega

    def load_com_objects(self, dpath):
        """Load Binary classifier compute objects for a single iteration of test and validation results

        Parameters
        ----------
        dpath : str
            dataset subdirectory path, e.g. "data/2022-02-03/results"

        Returns
        -------
        tuple
            tuple of test and validation compute objects for one iteration
        """
        T = super().load_compute_object(
            Com=ComputeBinary, alg="binary", res_path=f"{dpath}/results/test"
        )
        V = super().load_compute_object(
            Com=ComputeBinary,
            alg="binary",
            res_path=f"{dpath}/results/val",
            validation=True,
        )
        return (T, V)


class JwstCalScanner(MegaScanner):
    def __init__(self, perimeter="data/20??-*-*-*", primary=-1, **log_kws):
        super().__init__(
            perimeter=perimeter, primary=primary, name="JwstCalScanner", **log_kws
        )
        self.labels = []
        self.classes = []
        self.res_keys = dict(img3_reg=None)
        self.target = list(self.res_keys.keys())[0]
        self.data = self.select_dataset()
        self.mega = self.make_mega()
        self.kwargs = dict(index_col="img_name")
        self.decoder = KEYPAIR_DATA

    def scan_results(self):
        """Scans local disk for Computer object-generated results files and stores
        them as new Compute objects (according to the model type) in a nested dictionary.

        Returns
        -------
        HstCalScanner.mega dictionary attribute
            dictionary of model training results for each iteration found.
        """
        com_objects = []
        for d in self.datapaths:
            coms = self.load_com_objects(d)
            com_objects.append(coms)
            del coms

        for i in list(range(len(self.versions))):
            v = self.versions[i]
            (im3) = com_objects[i]
            self.mega[v]["res"] = dict(img3_reg=im3)
            del im3
        return self.mega

    def load_com_objects(self, dpath):
        """Loads Multi classifier and Regression compute objects (3 total) for a single iteration of results

        Parameters
        ----------
        dpath : str
            dataset subdirectory path, e.g. "data/2022-02-03/results"

        Returns
        -------
        tuple
            tuple of mem_bin, memory, wallclock compute objects for one iteration
        """
        im3 = super().load_compute_object(
            Com=ComputeRegressor, alg="linreg", res_path=f"{dpath}/results/img3_reg"
        )
        return im3
