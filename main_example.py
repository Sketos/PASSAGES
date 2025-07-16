import numpy as np

try:
    from astropy import units, \
                        constants
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
#
#     if os.path.isdir(ms):
#         sigma = getcol_wrapper(
#             ms=ms,
#             table="",
#             colname="SIGMA"
#         )
#     else:
#         raise IOError(
#             "{} does not exisxt".format(ms)
#         )
#
#     return sigma
#
#
# def export_sigma(ms, width, spw, contsub):
#
#     filename = "width_{}/sigma_spw_{}{}.fits".format(
#         width,
#         spw,
#         ".contsub" if contsub else ''
#     )
#     if os.path.isfile(filename):
#         print(
#             "{} already exists".format(filename)
#         )
#     else:
#         sigma = get_sigma(
#             ms="width_{}/{}".format(
#                 width,
#                 ms if ms.endswith(".statwt") else "{}.statwt".format(ms)
#             )
#         )
#
#         # sigma = np.average(
#         #     a=sigma,
#         #     axis=0
#         # )
#
#         num_chan = getcol_wrapper(
#             ms=ms,
#             table="SPECTRAL_WINDOW",
#             colname="NUM_CHAN"
#         )
#
#         if num_chan == width:
#             pass
#         else:
#             sigma = np.tile(
#                 A=sigma,
#                 reps=(
#                     int(num_chan / width), 1
#                 )
#             )
#
#         sigma = np.stack(
#             arrays=(sigma, sigma),
#             axis=-1
#         )
#
#         print(
#             "shape (sigma):", sigma.shape
#         )
#         fits.writeto(
#             filename=filename,
#             data=sigma,
#             overwrite=True
#         )

def get_frequencies(uid, field, spw):
    ms = "{}_field_{}_spw_{}.ms.split.cal".format(
        uid,
        field,
        spw
    )
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


def export_frequencies(uid, field, spw):
    chan_freq = get_frequencies(
        uid=uid,
        field=field,
        spw=spw
    )
    filename = "./{}_spw_{}_frequencies".format(
        uid,
        spw
    )
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
    antennas = get_antennas(
        ms=ms
    )
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
#     return np.asarray(time)
# def export_time(ms, filename):
#
#     time = get_time(
#         ms=ms
#     )
#
#     # NOTE:
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

if __name__ == "__main__":
    #uid = "A002_X11adad7_Xd8c1"
    uid = "A002_X11adad7_Xdfdb"
    field = "SPT0314-44"
    if not os.path.isdir(
        "uid___{}_{}.ms.split.cal".format(uid, field)
    ):
        if not os.path.isdir(
            "uid___{}.ms.split.cal".format(uid)
        ):
            raise NotImplementedError()
        else:
            split(
                vis="uid___{}.ms.split.cal".format(
                    uid
                ),
                outputvis="uid___{}_{}.ms.split.cal".format(
                    uid,
                    field
                ),
                keepmms=True,
                field=field,
                spw="",
                datacolumn="data",
                keepflags=False
            )
    spws = [
        "25",
        "27",
        "29",
        #"31",
    ]

    # NOTE:
    width = 960
    for spw in spws:
        if not os.path.isdir(
            "{}_{}_spw_{}_width_{}.ms.split.cal".format(
                "uid___" + uid,
                field,
                spw,
                width
            )
        ):
            split(
                vis="uid___{}_{}.ms.split.cal".format(
                    uid,
                    field
                ),
                outputvis="uid___{}_{}_spw_{}_width_{}.ms.split.cal".format(
                    uid,
                    field,
                    spw,
                    width
                ),
                keepmms=True,
                field=field,
                spw=spw,
                datacolumn="data",
                width=width,
                keepflags=False
            )

        # ========== #
        # NOTE: ...
        # ========== #
        filename_uv_wavelengths = "uv_wavelengths_{}_{}_spw_{}_width_{}".format(
            uid,
            field,
            spw,
            width,
        )
        if os.path.isfile(filename_uv_wavelengths + ".fits") or os.path.isfile(filename_uv_wavelengths + ".numpy"):
            pass
        else:
            export_uv_wavelengths(
                ms="uid___{}_{}_spw_{}_width_{}.ms.split.cal".format(
                    uid,
                    field,
                    spw,
                    width
                ),
                filename=filename_uv_wavelengths
            )
        # ========== #
        # END
        # ========== #

        # ========== #
        # NOTE: ...
        # ========== #
        filename_visibilities = "visibilities_{}_{}_spw_{}_width_{}".format(
            uid,
            field,
            spw,
            width,
        )
        if os.path.isfile(filename_visibilities + ".fits") or os.path.isfile(filename_visibilities + ".numpy"):
            pass
        else:
            export_visibilities(
                ms="uid___{}_{}_spw_{}_width_{}.ms.split.cal".format(
                    uid,
                    field,
                    spw,
                    width
                ),
                filename=filename_visibilities
            )
        # ========== #
        # END
        # ========== #

        # ========== #
        # NOTE: ...
        # ========== #
        filename = "antennas_{}_{}_spw_{}_width_{}".format(
            uid,
            field,
            spw,
            width
        )
        export_antennas(
            ms="uid___{}_{}_spw_{}_width_{}.ms.split.cal".format(
                uid,
                field,
                spw,
                width
            ),
            filename=filename
        )
        # ========== #
        # END
        # ========== #

        # ========== #
        # NOTE: ...
        # ========== #
        filename = "scans_{}_{}_spw_{}_width_{}".format(
            uid,
            field,
            spw,
            width
        )
        export_scans(
            ms="uid___{}_{}_spw_{}_width_{}.ms.split.cal".format(
                uid,
                field,
                spw,
                width
            ),
            filename=filename
        )
        # ========== #
        # END
        # ========== #
