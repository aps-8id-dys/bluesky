# Bluesky Instrument description

Describes the devices, plans, and other Python code supporting an instrument for
data acquisition with Bluesky.

description | configuration file
--- | ---
instrument customizations | `iconfig.yml`
interactive data collection | `collection.py`
bluesky-queueserver | `queueserver.py`

## Lambda2M IOC port map

This port map was generated from the bluesky command line:

```py
In [3]: lambda2M.visualize_asyn_digraph()

```

![lambda2M port map](./_resources/lambda2M-port-digraph.png)

It says that the data flows from the area detector camera (`LAMBDA2M`) to both
the `Image1` plugin and the `CODEC1` plugin, which compresses the data.  The
compressed data flows to both `FileHDF1` and `PVA1` plugins.

Similar info, but less descriptive, is available in text form:

```py
In [1]: lambda2M.get_asyn_digraph()
Out[1]: 
(<networkx.classes.digraph.DiGraph at 0x7f43ed111210>,
 {'LAMBDA2M': Lambda2MCam(prefix='8idLambda2m:cam1:', name='lambda2M_cam', parent='lambda2M', read_attrs=[], configuration_attrs=['acquire_period', 'acquire_time', 'image_mode', 'manufacturer', 'model', 'num_exposures', 'num_images', 'trigger_mode']),
  'FileHDF1': MyAD_EpicsFileNameHDF5Plugin(prefix='8idLambda2m:HDF1:', name='lambda2M_hdf1', parent='lambda2M', read_attrs=[], configuration_attrs=[]),
  'Image1': MyImagePlugin(prefix='8idLambda2m:image1:', name='lambda2M_image', parent='lambda2M', read_attrs=[], configuration_attrs=[]),
  'PVA1': MyPvaPlugin(prefix='8idLambda2m:Pva1:', name='lambda2M_pva', parent='lambda2M', read_attrs=[], configuration_attrs=[]),
  'CODEC1': CodecPlugin_V34(prefix='8idLambda2m:Codec1:', name='lambda2M_codec1', parent='lambda2M', read_attrs=[], configuration_attrs=[])})
```