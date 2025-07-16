import numpy as np

try:
    from astropy import (
        units,
        constants,
    )
    from astropy.io import fits
    astropy_is_imported = True
except:
    astropy_is_imported = False


def getcol_wrapper(ms, table, colname):
    if os.path.isdir(ms):
        tb.open(
            "{}/{}".format(ms, table)
        )
        col = np.squeeze(
            tb.getcol(colname)
        )

        tb.close()
    else:
        raise IOError(
            "{} does not exist".format(ms)
        )

    return col

def get_num_chan(ms):
    return getcol_wrapper(
        ms=ms,
        table="SPECTRAL_WINDOW",
        colname="NUM_CHAN"
    )

def get_spw_ids(ms):
    return getcol_wrapper(
        ms=ms,
        table="DATA_DESCRIPTION",
        colname="SPECTRAL_WINDOW_ID"
    )

def get_visibilities(ms):
    if os.path.isdir(ms):
        data = getcol_wrapper(
            ms=ms,
            table="",
            colname="DATA"
        )
    else:
        raise IOError(
            "{} does not exisxt".format(ms)
        )
    visibilities = np.stack(
        arrays=(data.real, data.imag),
        axis=-1
    )

    return visibilities


def export_visibilities(ms, filename):
    if os.path.isfile(filename):
        print(
            "{} already exists".format(filename)
        )
    else:
        visibilities = get_visibilities(ms=ms)
        print(
            "shape (visibilities):", visibilities.shape
        )
        if astropy_is_imported:
            fits.writeto(
                filename=filename + ".fits",
                data=visibilities,
                overwrite=True
            )
        else:
            with open(filename + ".numpy", 'wb') as file:
                np.save(file, visibilities)

def convert_array_to_wavelengths(array, frequency):
    if astropy_is_imported:
        array_converted = (
            (array * units.m) * (frequency * units.Hz) / constants.c
        ).decompose().value
    else:
        array_converted = array * frequency / 299792458.0

    return array_converted


def get_uv_wavelengths(ms):
    if os.path.isdir(ms):
        uvw = getcol_wrapper(
            ms=ms,
            table="",
            colname="UVW"
        )
    else:
        raise IOError(
            "{} does not exisxt".format(ms)
        )
    chan_freq = getcol_wrapper(
        ms=ms,
        table="SPECTRAL_WINDOW",
        colname="CHAN_FREQ"
    )
    chan_freq_shape = np.shape(chan_freq)
    if np.shape(chan_freq):
        u_wavelengths, v_wavelengths = np.zeros(
            shape=(
                2,
                chan_freq_shape[0],
                uvw.shape[1]
            )
        )
        for i in range(chan_freq_shape[0]):
            u_wavelengths[i, :] = convert_array_to_wavelengths(array=uvw[0, :], frequency=chan_freq[i])
            v_wavelengths[i, :] = convert_array_to_wavelengths(array=uvw[1, :], frequency=chan_freq[i])
    else:
        u_wavelengths = convert_array_to_wavelengths(array=uvw[0, :], frequency=chan_freq)
        v_wavelengths = convert_array_to_wavelengths(array=uvw[1, :], frequency=chan_freq)
    uv_wavelengths = np.stack(
        arrays=(u_wavelengths, v_wavelengths),
        axis=-1
    )

    return uv_wavelengths


def export_uv_wavelengths(ms, filename):
    if os.path.isfile(filename):
        print(
            "{} already exists".format(filename)
        )
    else:
        uv_wavelengths = get_uv_wavelengths(ms=ms)
        print(
            "shape (uv_wavelengths):", uv_wavelengths.shape
        )
        if astropy_is_imported:
            fits.writeto(
                filename=filename + ".fits",
                data=uv_wavelengths,
                overwrite=True
            )
        else:
            with open(filename + ".numpy", 'wb') as file:
                np.save(file, uv_wavelengths)

# def get_sigma(ms):
#     if os.path.isdir(ms):
#         sigma = getcol_wrapper(
#             ms=ms,
#             table="",
#             colname="SIGMA"
#         )
#         chan_freq = getcol_wrapper(
#             ms=ms,
#             table="SPECTRAL_WINDOW",
#             colname="CHAN_FREQ"
#         )
#         sigma = np.tile(
#             sigma[:, np.newaxis, :], (1, len(chan_freq), 1)
#         )
#     else:
#         raise IOError(
#             "{} does not exisxt".format(ms)
#         )
#     return np.stack(
#         arrays=(sigma, sigma),
#         axis=-1
#     )
# def export_sigma(ms, filename):
#     if os.path.isfile(filename):
#         print(
#             "{} already exists".format(filename)
#         )
#     else:
#         sigma = get_sigma(ms=ms)
#         print(
#             "shape (sigma):", sigma.shape
#         )
#         if astropy_is_imported:
#             fits.writeto(
#                 filename=filename + ".fits",
#                 data=sigma,
#                 overwrite=True
#             )
#         else:
#             with open(filename + ".numpy", 'wb') as file:
#                 np.save(file, sigma)

def get_frequencies(ms):
    if os.path.isdir(ms):
        chan_freq = getcol_wrapper(
            ms=ms,
            table="SPECTRAL_WINDOW",
            colname="CHAN_FREQ"
        )
    else:
        raise IOError(
            "The directory {} does not exist".format(ms)
        )

    return chan_freq


def export_frequencies(ms, filename):
    chan_freq = get_frequencies(ms=ms)
    if astropy_is_imported:
        fits.writeto(
            filename="{}.fits".format(filename),
            data=chan_freq
        )
    else:
        with open("{}.numpy".format(filename), 'wb') as file:
            np.save(file, chan_freq)

def get_antennas(ms):
    antenna1 = getcol_wrapper(
        ms=ms,
        table="",
        colname="ANTENNA1"
    )
    antenna2 = getcol_wrapper(
        ms=ms,
        table="",
        colname="ANTENNA2"
    )

    return np.array([
        antenna1,
        antenna2
    ])

def export_antennas(ms, filename):
    if not os.path.isdir(ms):
        raise IOError("The ms does not exist.")
    antennas = get_antennas(
        ms=ms
    )
    print(antennas.shape)
    if astropy_is_imported:
        filename += ".fits"
    else:
        filename += ".numpy"
    if filename.endswith(".fits"):
        fits.writeto(
            filename=filename,
            data=antennas,
            overwrite=True
        )
    else:
        with open(filename, 'wb') as file:
            np.save(file, antennas)

# def get_time(ms):
#     time = getcol_wrapper(
#         ms=ms,
#         table="",
#         colname="TIME"
#     )
#
#     return np.asarray(time)
#
# def export_time(ms, filename):
#     time = get_time(
#         ms=ms
#     )
#     if astropy_is_imported:
#         filename += ".fits"
#     else:
#         filename += ".numpy"
#     if filename.endswith(".fits"):
#         fits.writeto(
#             filename=filename,
#             data=time,
#             overwrite=True
#         )
#     else:
#         with open(filename, 'wb') as file:
#             np.save(file, time)

def get_scans(ms):
    scans = getcol_wrapper(
        ms=ms,
        table="",
        colname="SCAN_NUMBER"
    )
    return np.asarray(scans)

def export_scans(ms, filename):
    scans = get_scans(
        ms=ms
    )
    if astropy_is_imported:
        filename += ".fits"
    else:
        filename += ".numpy"
    if filename.endswith(".fits"):
        fits.writeto(
            filename=filename,
            data=scans,
            overwrite=True
        )
    else:
        with open(filename, 'wb') as file:
            np.save(file, scans)

if __name__ == "__main__": # NOTE: spw == "31" has an emission line
    uid = "A002_X11adad7_Xdfdb"
    field = "SPT0314-44"
    if True:
        #width = 15
        width = 30
        outputvis = "uid___{}_width_{}.ms.split.cal.contsub".format(
            uid,
            width
        )
        if not os.path.isdir(outputvis):
            split(
                vis="uid___{}.ms.split.cal.contsub".format(
                    uid,
                ),
                outputvis=outputvis,
                keepmms=True,
                field=field,
                spw="0",
                datacolumn="data",
                width=width,
                keepflags=False
            )

        # ========== #
        # NOTE: ...
        # ========== #
        filename_uv_wavelengths = "uv_wavelengths_{}_{}_spw_31_width_{}_contsub".format(
            uid,
            field,
            width,
        )
        if os.path.isfile(filename_uv_wavelengths + ".fits") or os.path.isfile(filename_uv_wavelengths + ".numpy"):
            pass
        else:
            export_uv_wavelengths(
                ms=outputvis,
                filename=filename_uv_wavelengths
            )
        # ========== #
        # END
        # ========== #

        # ========== #
        # NOTE: ...
        # ========== #
        filename_visibilities = "visibilities_{}_{}_spw_31_width_{}_contsub".format(
            uid,
            field,
            width,
        )
        if os.path.isfile(filename_visibilities + ".fits") or os.path.isfile(filename_visibilities + ".numpy"):
            pass
        else:
            export_visibilities(
                ms=outputvis,
                filename=filename_visibilities
            )
        # ========== #
        # END
        # ========== #

        # ========== #
        # NOTE: ...
        # ========== #
        filename = "antennas_{}_{}_spw_31_width_{}_contsub".format(
            uid,
            field,
            width
        )
        if os.path.isfile(filename + ".fits") or os.path.isfile(filename + ".numpy"):
            pass
        else:
            export_antennas(
                ms=outputvis,
                filename=filename
            )
        # ========== #
        # END
        # ========== #

        # ========== #
        # NOTE: ...
        # ========== #
        filename = "scans_{}_{}_spw_31_width_{}_contsub".format(
            uid,
            field,
            width
        )
        if os.path.isfile(filename + ".fits") or os.path.isfile(filename + ".numpy"):
            pass
        else:
            export_scans(
                ms=outputvis,
                filename=filename
            )
        # ========== #
        # END
        # ========== #

        # ========== #
        # NOTE: ...
        # ========== #
        filename = "frequencies_{}_{}_spw_31_width_{}_contsub".format(
            uid,
            field,
            width
        )
        if os.path.isfile(filename + ".fits") or os.path.isfile(filename + ".numpy"):
            pass
        else:
            export_frequencies(
                ms=outputvis,
                filename=filename
            )
        # ========== #
        # END
        # ========== #
