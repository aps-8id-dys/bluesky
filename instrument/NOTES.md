# NOTES of the next things to do

- start with the data written in a directory
- write the HDF5 metadata file for the workflow
  - workflow we used before has PVs that are no longer available
  - Re-use old code or start again?
    - Are PVs the only modifications?
  - We can start fresh using a minimal version of HDF5.
    - [ ] One way is to write everything into the root of the HDF5 file.
    - [x] Another way is to start with minimum NeXus structure (no application definition).
    - [ ] Another way is to start with minimum Data Exchange structure.
- call the workflow using the (new) Bluesky API from apstools
- High priority is the Bluesky write the data into the correct user directory.
  - Area detector is configured to write its image files to this directory.
    - Adds metadata from the attributes.xml file.  (defines the PVs to be gathered)
    - Writes HDF5 with structure from the layout.xml file. (describes where to write the PVs)
  - Bluesky plan would write its HDF5 file to this directory.
    - One metadata file would be re-used for many raw image files.
    - If put everything all in one file, file would be too big.
    - Expect users will not take this data home.
    - Raw data format must remain flexible for performance reasons (too fast for one file, for example)
- How is the correct user directory defined?
  - Pass this as an argument (such as `A002_silica*`) to the plan.
  - This is **within** a beamline-defined directory.
- What about the beamline-defined directory?
  - This might be a `initialize_user()` plan
  - Parameters might include:
    - beamline-defined directory
      - Make a good recommendation (default).
      - Test early and fail if not correct.
    - ESAF & Proposal #
      - Both ESAF and proposal will pull user names and title
    - Commissioning does not get these automatically
      - so need more parameters possible, such as:
        - user name
        - sample
        - title
        - ...
  - Store all the user-oriented beamtime information in an `ophyd.Device` structure
    - For starters, just make Python objects. (`ophyd.Signal`)
    - Eventually, this could be connected with EPICS PVs (`ophyd.EpicsSignal`)
- Will we continue to use SPEC data files?
  - No, rely on bluesky's databases.
  - BCDA will develop and provide tool to identify runs and export to a file.
- How do we communicate information about the beamtime's data to the user (such as at the end of their beam time).
- What should Bluesky write into the HDF5 metadata file?
  - Look at the previous one for ideas.
  - Devices and Signals defined via ophyd.
  - Make a PV file that beamline staff can revise and reload
    - Bunch of PVs: motors, detectors (that are not known to Bluesky)
- Should the _results_ file (with $g_2$) also be made NeXus?
  - not important to Bluesky (Miaoqi could respond)
