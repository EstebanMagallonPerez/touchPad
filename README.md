# TrackPad Controller
I had a problem... I cut a hole in my desk and put a touchscreen in it. Touchscreens dont work as a trackpad so I made this.

## Setup

Follow the steps [here](https://www.orangecoat.com/how-to/use-pyusb-to-find-vendor-and-product-ids-for-usb-devices) to get your touchscreens vendor, and product id. You will likely need to install a driver on your touchscreen to be able to read the messages through python. 

Update the idVendor, and idProduct variables in the code to match your vendor and product IDs.

Then run it, and it should work... probably. Good luck
