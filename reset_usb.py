#!/usr/bin/env python
import argparse
import os
import sys
from subprocess import Popen, PIPE
import fcntl


def create_pci_list():
    pci_usb_list = list()
    try:
        lspci_out = Popen('lspci -Dvmm', shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True).stdout.read().strip().decode('utf-8')
        pci_devices = lspci_out.split('%s%s' % (os.linesep, os.linesep))
        for pci_device in pci_devices:
            device_dict = dict()
            categories = pci_device.split(os.linesep)
            for category in categories:
                key, value = category.split('\t')
                device_dict[key[:-1]] = value.strip()
            if 'USB' not in device_dict['Class']:
                continue
            for root, dirs, files in os.walk('/sys/bus/pci/drivers/'):
                slot = device_dict['Slot']
                if slot in dirs:
                    device_dict['path'] = os.path.join(root, slot)
                    break
            pci_usb_list.append(device_dict)
    except Exception as ex:
        print('Failed to list pci devices! Error: %s' % ex)
        sys.exit(-1)
    return pci_usb_list


def create_usb_list():
    device_list = list()
    try:
        lsusb_out = Popen('lsusb -v', shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, close_fds=True).stdout.read().strip().decode('utf-8')
        usb_devices = lsusb_out.split('%s%s' % (os.linesep, os.linesep))
        for device_categories in usb_devices:
            if not device_categories:
                continue
            categories = device_categories.split(os.linesep)
            device_stuff = categories[0].strip().split()
            bus = device_stuff[1]
            device = device_stuff[3][:-1]
            device_dict = {'bus': bus, 'device': device}
            device_info = ' '.join(device_stuff[6:])
            device_dict['description'] = device_info
            for category in categories:
                if not category:
                    continue
                categoryinfo = category.strip().split()
                if categoryinfo[0] == 'iManufacturer':
                    manufacturer_info = ' '.join(categoryinfo[2:])
                    device_dict['manufacturer'] = manufacturer_info
                if categoryinfo[0] == 'iProduct':
                    device_info = ' '.join(categoryinfo[2:])
                    device_dict['device'] = device_info
            path = '/dev/bus/usb/%s/%s' % (bus, device)
            device_dict['path'] = path

            device_list.append(device_dict)
    except Exception as ex:
        print('Failed to list usb devices! Error: %s' % ex)
        sys.exit(-1)
    return device_list


# echo -n "0000:39:00.0" | tee /sys/bus/pci/drivers/xhci_hcd/unbind;echo -n "0000:39:00.0" | tee /sys/bus/pci/drivers/xhci_hcd/bind
def reset_pci_usb_device(dev_path):
    folder, slot = os.path.split(dev_path)
    try:
        fp = open(os.path.join(folder, 'unbind'), 'wt')
        fp.write(slot)
        fp.close()
        fp = open(os.path.join(folder, 'bind'), 'wt')
        fp.write(slot)
        fp.close()
        print('Successfully reset %s' % dev_path)
        sys.exit(0)
    except Exception as ex:
        print('Failed to reset device! Error: %s' % ex)
        sys.exit(-1)


def reset_usb_device(dev_path):
    USBDEVFS_RESET = 21780
    try:
        f = open(dev_path, 'w', os.O_WRONLY)
        fcntl.ioctl(f, USBDEVFS_RESET, 0)
        print('Successfully reset %s' % dev_path)
        sys.exit(0)
    except Exception as ex:
        print('Failed to reset device! Error: %s' % ex)
        sys.exit(-1)

def main():
    parser = argparse.ArgumentParser(description='Reset USB device')
    parser.add_argument('--list', action='store_true', help='List all USB devices')
    parser.add_argument('--listpci', action='store_true', help='List all PCI USB devices')
    parser.add_argument('--path', help='Reset USB device using path /dev/bus/usb/XXX/YYY')
    parser.add_argument('--search', help='Search for USB device using the search terms within the search string returned by list and reset matching device')
    parser.add_argument('--pathpci', help='Reset PCI USB device using path /sys/bus/pci/drivers/.../XXXX:XX:XX.X')
    parser.add_argument('--searchpci', help='Search for PCI USB device using the search terms within the search string returned by listpci and reset matching device')
    args = parser.parse_args()

    if args.listpci:
        pci_usb_list = create_pci_list()
        for device in pci_usb_list:
            print('path=%s' % device['path'])
            print('    manufacturer=%s' % device['SVendor'])
            print('    device=%s' % device['SDevice'])
            print('    search string=%s %s' % (device['SVendor'], device['SDevice']))
    elif args.list:
        usb_list = create_usb_list()
        for device in usb_list:
            print('path=%s' % device['path'])
            print('    description=%s' % device['description'])
            print('    manufacturer=%s' % device['manufacturer'])
            print('    device=%s' % device['device'])
            print('    search string=%s %s %s' % (device['description'], device['manufacturer'], device['device']))
    elif args.pathpci:
        reset_pci_usb_device(args.pathpci)
    elif args.searchpci:
        pci_usb_list = create_pci_list()
        for device in pci_usb_list:
            text = '%s %s' % (device['SVendor'], device['SDevice'])
            if args.searchpci in text:
                reset_pci_usb_device(device['path'])
        print('Failed to find device!')
        sys.exit(-1)
    elif args.path:
        reset_usb_device(args.path)
    elif args.search:
        usb_list = create_usb_list()
        for device in usb_list:
            text = '%s %s %s' % (device['description'], device['manufacturer'], device['device'])
            if args.search in text:
                reset_usb_device(device['path'])
        print('Failed to find device!')
        sys.exit(-1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
