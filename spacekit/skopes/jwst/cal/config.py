"""Configuration for JWST calibration reprocessing machine learning projects.
"""
GENKEYS = [
    "PROGRAM", # Program number
    "OBSERVTN", # Observation number
    "BKGDTARG", # Background target
    "VISITYPE", #  Visit type
    "TSOVISIT", # Time Series Observation visit indicator
    "TARGNAME", # Standard astronomical catalog name for target
    "TARG_RA", # Target RA at mid time of exposure
    "TARG_DEC", # Target Dec at mid time of exposure
    "INSTRUME", # Instrument used to acquire the data
    "DETECTOR", # Name of detector used to acquire the data
    "FILTER", # Name of the filter element used
    "PUPIL", # Name of the pupil element used  
    "EXP_TYPE", # Type of data in the exposure
    "CHANNEL", # Instrument channel 
    "SUBARRAY", # Subarray used
    "NUMDTHPT", # Total number of points in pattern
    "GS_RA",  #  guide star right ascension                     
    "GS_DEC", # guide star declination 
]

SCIKEYS = [
    "RA_REF",
    "DEC_REF",
    "CRVAL1",
    "CRVAL2",
]

COLUMN_ORDER = {
   "asn": [
       'instr',
       'detector',
       'exp_type',
       'visitype',
       'filter',
       'pupil',
       'channel',
       'subarray',
       'bkgdtarg',
       'tsovisit',
       'nexposur',
       'numdthpt',
       'offset',
       'max_offset',
       'mean_offset',
       'sigma_offset',
       'err_offset',
       'sigma1_mean',
       'frac',
   ]
}

NORM_COLS = {"asn": [],}

RENAME_COLS = {"asn": [],}

X_NORM = {"asn": []}

KEYPAIR_DATA={
    "detector": {
        "0": "NONE", "1": "NRS2", "2": "NRS1", "3": "NRCBLONG", "4": "NRCB4", "5": "NRCB3", "6": "NRCB2", "7": "NRCB1", "8": "NRCA1", "9": "NRCA2", "10": "NRCA3", "11": "NRCA4", "12": "NRCALONG", "13": "NIS", "14": "MIRIMAGE", "15": "MIRIFUSHORT", "16": "MIRIFULONG", "17": "GUIDER2", "18": "GUIDER1", "19": "NRCA1|NRCA2|NRCA3|NRCA4", "20": "GUIDER1|GUIDER2", "21": "NRCB1|NRCB2|NRCB3|NRCB4", "22": "NRCALONG|NRCBLONG", "23": "NRCA1|NRCA2|NRCA3|NRCA4|NRCB1|NRCB2|NRCB3|NRCB4", "24": "NRCA1|NRCA3", "25": "MIRIFULONG|MIRIFUSHORT", "26": "NRS1|NRS2", "27": "MIRIFULONG|MIRIFUSHORT|MIRIMAGE", "28": "NRCB1|NRCBLONG", "29": "NRCA1|NRCA3|NRCALONG", "30": "NRCB2|NRCB4"
    },
    "channel": {
        "0": "NONE", "1": "LONG", "2": "SHORT", "3": "12", "4": "34"
    },
    "exp_type": {
        "0": "NONE", "1": "NRS_MSASPEC", "2": "NRC_IMAGE", "3": "NRS_FIXEDSLIT", "4": "NIS_IMAGE", "5": "NIS_WFSS", "6": "MIR_IMAGE", "7": "MIR_MRS", "8": "NRS_IFU", "9": "FGS_IMAGE", "10": "FGS_INTFLAT", "11": "FGS_FOCUS", "12": "NIS_AMI", "13": "MIR_FLATIMAGE-EXT", "14": "MIR_LRS-FIXEDSLIT", "15": "MIR_LRS-SLITLESS", "16": "MIR_4QPM", "17": "MIR_LYOT", "18": "MIR_FLATIMAGE", "19": "NRC_LED", "20": "NRC_DARK", "21": "NRC_TSIMAGE", "22": "NRC_TSGRISM", "23": "NRC_CORON", "24": "NRC_GRISM", "25": "NIS_LAMP", "26": "NIS_EXTCAL", "27": "NIS_DARK", "28": "NIS_SOSS", "29": "NRS_LAMP", "30": "NRS_BRIGHTOBJ", "31": "NRS_AUTOWAVE", "32": "NRS_AUTOFLAT", "33": "NRS_MIMF", "34": "MIR_FLATMRS", "35": "NRS_AUTOWAVE|NRS_IFU", "36": "MIR_LRS-FIXEDSLIT|NIS_SOSS", "37": "NRC_WFSS|NRS_AUTOFLAT|NRS_AUTOWAVE", "38": "NRS_AUTOFLAT|NRS_AUTOWAVE|NRS_FIXEDSLIT", "39": "NRC_WFSS"
    },
    "visitype": {
        "0": "NONE", "1": "PARALLEL_PURE", "2": "PARALLEL_SLEW_CALIBRATION", "3": "PRIME_TARGETED_FIXED", "4": "PRIME_TARGETED_MOVING", "5": "PRIME_UNTARGETED", "6": "PRIME_WFSC_ROUTINE", "7": "PRIME_WFSC_SENSING_CONTROL", "8": "PRIME_WFSC_SENSING_ONLY", "9": ".+WFSC.+"
    },
    "visitype_c": {
        "0": {"N": "NONE"}, "1": {"PP": "PARALLEL_PURE"}, "2": {"PSC": "PARALLEL_SLEW_CALIBRATION"}, "3": {"PTF": "PRIME_TARGETED_FIXED"}, "4": {"PTM": "PRIME_TARGETED_MOVING"}, "5": {"PU": "PRIME_UNTARGETED"}, "6": {"PWR": "PRIME_WFSC_ROUTINE"}, "7": {"PWSC": "PRIME_WFSC_SENSING_CONTROL"}, "8": {"PWSO": "PRIME_WFSC_SENSING_ONLY"}, "9": {"W": ".+WFSC.+"}
    },
    "filter": {
        "0": "NONE", "1": "F140X", "2": "F277W", "3": "F115W", "4": "F150W", "5": "F356W", "6": "F070W", "7": "F444W", "8": "CLEAR", "9": "GR150R", "10": "GR150C", "11": "F200W", "12": "F090W", "13": "F410M", "14": "F335M", "15": "F770W", "16": "F1280W", "17": "F070LP", "18": "F170LP", "19": "F290LP", "20": "F1130W", "21": "F560W", "22": "F100LP", "23": "F1500W", "24": "F1800W", "25": "F110W", "26": "F2100W", "27": "F2550W", "28": "F210M", "29": "F480M", "30": "F212N", "31": "F250M", "32": "F150W2", "33": "F322W2", "34": "F187N", "35": "F140M", "36": "F1000W", "37": "F1065C", "38": "F1550C", "39": "F1140C", "40": "F2300C", "41": "OPAQUE", "42": "F2550WR", "43": "P750L", "44": "FND", "45": "WLP4", "46": "F430M", "47": "F460M", "48": "F182M", "49": "F300M", "50": "F360M", "51": "F380M"
    },
    "pupil": {
        "0": "NONE", "1": "CLEAR", "2": "F115W", "3": "F150W", "4": "F200W", "5": "CLEARP", "6": "NRM", "7": "F405N", "8": "F164N", "9": "F470N", "10": "F323N", "11": "MASKIPR", "12": "FLAT", "13": "MASKRND", "14": "F466N", "15": "GDHS60", "16": "GDHS0", "17": "MASKBAR", "18": "F162M", "19": "WLP8", "20": "WLM8", "21": "GRISMR", "22": "F158M", "23": "GR700XD", "24": "F090W", "25": "F140M", "26": "GRISMC"
    }, 
    "grating": {
        "0": "NONE", "1": "MIRROR", "2": "PRISM", "3": "G140M", "4": "G235M", "5": "G395M", "6": "G395H", "7": "G140H", "8": "G235H"
    }, 
    "subarray": {
        "0": "NONE", "1": "FULL", "2": "SUB2048", "3": "SUB256", "4": "SUB32", "5": "SUBTAAMI", "6": "SUB64", "7": "SLITLESSPRISM", "8": "MASK1065", "9": "MASK1140", "10": "MASK1550", "11": "MASKLYOT", "12": "SUB640", "13": "SUBGRISM256", "14": "SUB32TATSGRISM", "15": "SUB32TATS", "16": "SUB64P", "17": "SUB320", "18": "SUB160", "19": "SUB400P", "20": "SUBFSA430R", "21": "SUBNDALWBS", "22": "SUBNDA430R", "23": "SUBNDASWBS", "24": "SUBNDA210R", "25": "SUBNDALWBL", "26": "SUBFSALWB", "27": "SUBNDA335R", "28": "SUBFSA335R", "29": "SUBFSASWB", "30": "SUBFSA210R", "31": "SUB128", "32": "WFSS64C", "33": "WFSS128R", "34": "SUBAMPCAL", "35": "SUB80", "36": "WFSS128C", "37": "WFSS64R", "38": "SUBSTRIP256", "39": "SUBSTRIP96", "40": "SUBTASOSS", "41": "SUB512", "42": "ALLSLITS", "43": "SUBS200A1", "44": "SUBS400A1", "45": "SUBS200A2", "46": "SUB96DHSPILA", "47": "SUB160P", "48": "SUB64FP1A", "49": "SUB320A335R", "50": "SUBGRISM64", "51": "SUB320ALWB", "52": "SUB320A430R", "53": "BRIGHTSKY", "54": "SUB640A210R", "55": "SUBGRISM128", "56": "SUB512S", "57": "SUB640ASWB"
    },
}
