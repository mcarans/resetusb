List USB devices and reset one of them from command line

Usage: 

    python reset_usb.py help : Show this help
    sudo python reset_usb.py list : List all USB devices
    sudo python reset_usb.py path /dev/bus/usb/XXX/YYY : Reset USB device using path /dev/bus/usb/XXX/YYY
    sudo python reset_usb.py search "search terms" : Search for USB device using the search terms within the search string returned by list and reset matching device
    sudo python reset_usb.py listpci : List all PCI USB devices
    sudo python reset_usb.py pathpci /sys/bus/pci/drivers/.../XXXX:XX:XX.X : Reset PCI USB device using path
    sudo python reset_usb.py searchpci "search terms" : Search for PCI USB device using the search terms within the search string returned by listpci and reset matching device       

