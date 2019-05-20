# hylink

Hylink is a Python library which allows transmit/receive access to Hytera DMR repeaters by providing a wrapper around the
UDP "dispatcher" (also known as ADK or HRNP) protocols.

Hylink is licenced under the GNU LGPL v3 (or any later version) which permits its use in closed-source applications provided
any changes made to Hylink are fed back upstream (fork this repository and open a pull request)

## Project status

Hylink is under development and should be considered alpha-quality at this stage. The API may change without notice.

## Thanks

Hylink would not have been possible without the hard work and contributions of the following people:

  * Lars DK7LST's [Hytbridge](https://github.com/dk7lst/HytBridge) project gave the initial kickstart to this project and some insight into the UDP protoco.
  * ON4ABS and HAM-DMR RST's [DMR Synchronised Filesystem](https://sites.google.com/site/hamdmrrst/cursus/dmr-synchronized-file-system) provided a lot of isight into Hytera's higher-level protocols.
  * Furcation Ltd. for allowing me to borrow their RD985 radio repeater to develop Hylink.
