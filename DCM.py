# -*- coding: utf-8 -*-

import sys, os, math, argparse, pydicom
try:
  import pkg_resources.py2_warn
except Exception as e: pass
from PyVutils import File, DCM, Others

__package__ = "DICOM Tools"
__version__ = "1.0.0"

OPERATIONS = {
  "difference": (set.difference, "~"),
  "intersection": (set.intersection, "="),
  "compare": (set.intersection, "#"),
  "fulfil": (set.difference, "+"),
  "view": (None, "v"),
}

NPADDING = 45 # name padding
VPADDING = 70 # value padding

def dcm_fn(operator, sign, file_path_1, file_path_2):
  # Perform an operation to 2 dicom files
  ds_1 = DCM.Load(file_path_1, force=True)
  ds_2 = DCM.Load(file_path_2, force=True)

  set_ds_1 = set(ds_1.keys())
  set_ds_2 = set(ds_2.keys())

  l = sorted(list(operator(set_ds_1, set_ds_2)))

  for e in l:
    attr = ds_1[e]
    try:
      if type(attr.value) is bytes:
        print(f"[{sign}]", f"{attr.tag} {attr.name} {' '*(attr.descripWidth - len(attr.name) - 1)} {attr.VR}: <bin:{len(attr.value)}>")
      else: print(f"[{sign}]", attr)
    except Exception as e: print(f"[{sign}]", f"{attr.tag} ??? {' '*(attr.descripWidth - 3)}???")

  return

def dcm_view(operator, sign, file_path):
  # View a dicom file
  ds = DCM.Load(file_path, force=True)

  set_ds = set(ds.keys())

  l = sorted(list(set_ds))

  for e in l:
    attr = ds[e]
    try:
      if type(attr.value) is bytes:
        print(f"[{sign}]", f"{attr.tag} {attr.name} {' '*(attr.descripWidth - len(attr.name) - 1)} {attr.VR}: <bin:{len(attr.value)}>")
      else: print(f"[{sign}]", attr)
    except Exception as e: print(f"[{sign}]", f"[{attr.tag} ??? {' '*(attr.descripWidth - 3)}???")

def dcm_compare(operator, sign, file_path_1, file_path_2):
  # Perform an operation to 2 dicom files
  ds_1 = DCM.Load(file_path_1, force=True)
  ds_2 = DCM.Load(file_path_2, force=True)

  set_ds_1 = set(ds_1.keys())
  set_ds_2 = set(ds_2.keys())

  l = sorted(list(operator(set_ds_1, set_ds_2)))

  for e in l:
    attr_1, attr_2 = ds_1[e], ds_2[e]
    attr = attr_1
    name_padding = ' '*(NPADDING - len(attr.name) - 1)
    val_padding  = ' '*(VPADDING - len(str(attr_1.value)) - 1)
    try:
      if type(attr.value) is bytes:
        val_1 = f"<bin:{len(attr_1.value)}>"
        val_2 = f"<bin:{len(attr_1.value)}>"
        if val_1 != val_2:
          val_padding  = ' '*(VPADDING - len(val_1) - 1)
          print(f"[{sign}]", f"{attr.tag} {attr.name} {name_padding} {attr.VR}: {val_1}{val_padding} | {val_2}")
      elif type(attr.value) is pydicom.sequence.Sequence:
        val_1 = f"<SEQUENCE, len:{len(attr_1.value)}>"
        val_2 = f"<SEQUENCE, len:{len(attr_1.value)}>"
        val_padding = ' '*(VPADDING - len(val_1) - 1)
        print(f"[{sign}]", f"{attr.tag} {attr.name} {name_padding} {attr.VR}: {val_1}{val_padding} | {val_2}")
      else:
        val_1, val_2 = attr_1.value, attr_2.value
        equal = val_1 == val_2
        try:
          v1 = float(val_1)
          v2 = float(val_2)
          val_1, val_2 = v1, v2
          equal = math.isclose(val_1, val_2, abs_tol=1e-3)
        except Exception as e: pass
        if not equal:
          print(f"[{sign}]", f"{attr.tag} {attr.name} {name_padding} {attr.VR}: {attr_1.value}{val_padding} | {attr_2.value}")
    except Exception as e: print(f"[{sign}]", f"{attr.tag} ??? {' '*(attr.descripWidth - 3)}???")

  return

def dcm_fulfil(operator, sign, file_path_src, file_path_dst, addable_tags = ""):
  # Perform fulfil missing tags for the second dicom file from the first dicom file
  file_path_1 = file_path_src
  file_path_2 = file_path_dst

  ds_1 = DCM.Load(file_path_1, force=True)
  ds_2 = DCM.Load(file_path_2, force=True)

  set_ds_1 = set(ds_1.keys())
  set_ds_2 = set(ds_2.keys())

  tags = sorted(list(operator(set_ds_1, set_ds_2)))

  _addable_tags = addable_tags.replace(' ', '').split("|")
  the_addable_tags = []
  for e in _addable_tags:
    if len(e) == len("(gggg,eeee)"): the_addable_tags.append(e)

  for tag in tags:
    tag_s = str(tag).replace(' ', '')
    if the_addable_tags:
      if not tag_s in the_addable_tags: continue
    status = None
    try:
      ds_2[tag] = ds_1[tag]
      status = "OK"
    except: status = "SUCCEED"
    print(f"[{sign}]", f"{tag} -> Add {status}")

  file_path_noext, ext = os.path.splitext(file_path_dst)
  file_path_new = f"{file_path_noext}(new){ext}"

  status = None
  try:
    ds_2.save_as(file_path_new)
    status = "SUCCEED"
  except: status = "FAILED"
  print(f"File Saved {status} at `{file_path_new}`")

  return

def main():
  print(f"{__package__} {__version__}")

  parser = argparse.ArgumentParser(description=__package__)
  parser.add_argument("-a", "--action", type=str, required=True, default="", choices=OPERATIONS.keys(), help="The action to do")
  parser.add_argument("-f", "--files", type=str, required=True, nargs="+", help="Set of 2 or many files. Eg. \"path\\1.dcm\" \"path\\2.dcm\"")
  parser.add_argument("-t", "--tags", type=str, required=False, default="", help="Set of addable tags. Eg. \"(0008, 002a)|(0008, 0031)\"")
  parser.add_argument("-v", "--verbose", default=False, action="store_true", help="Print the verbose information")
  args = parser.parse_args()

  action = args.action.lower()
  operator, sign = OPERATIONS.get(action)

  if action in ["difference", "intersection", "fulfil"]:
    if len(args.files) != 2:
      print(f"{sys.argv[0]}: error: required 2 dicom files")
      return
    if action == "fulfil": dcm_fulfil(operator, sign, args.files[0], args.files[1], args.tags)
    else: dcm_fn(operator, sign, args.files[0], args.files[1])
  elif action == "compare": dcm_compare(operator, sign, args.files[0], args.files[1])
  elif action == "view": dcm_view(operator, sign, args.files[0])
  else: pass

  return True

if __name__ == "__main__":
  try: sys.exit(main())
  except (Exception, KeyboardInterrupt): Others.LogException(sys.exc_info())
