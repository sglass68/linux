# SPDX-License-Identifier: GPL-2.0+
#

# Xilinx XADC device driver

from kschema import NodeDesc, PropBool, PropClocks, PropInt, PropIntList, PropInterrupts, PropReg, PropStringList

schema = [
    NodeDesc('xilinx-xadc', ['xlnx,zynq-xadc-1.00.a', 'xlnx,axi-xadc-1.00.a'], False, desc=
            'This binding document describes the bindings for both of them since the'
            'bindings are very similar. The Xilinx XADC is a ADC that can be found in the'
            'series 7 FPGAs from Xilinx. The XADC has a DRP interface for communication.'
            'Currently two different frontends for the DRP interface exist. One that is only'
            'available on the ZYNQ family as a hardmacro in the SoC portion of the ZYNQ. The'
            'other one is available on all series 7 platforms and is a softmacro with a AXI'
            'interface. This binding document describes the bindings for both of them since'
            'the bindings are very similar.', elements=[
        PropReg(required=True, 
            desc='Address and length of the register set for the device'),
        PropInterrupts(required=True, 
            desc='Interrupt for the XADC control interface.'),
        PropClocks(required=True, 
            desc='When using the ZYNQ this must be the ZYNQ PCAP clock,'
            'when using the AXI-XADC pcore this must be the clock that provides the'
            'clock to the AXI bus interface of the core.'),
        PropStringList('xlnx,external-mux', str_pattern='none|single|dual',
            desc=''),
        PropIntList('xlnx,external-mux-channel', valid_list='0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|16|1|2|3|4|5|6|8',
            desc='Configures which pair of pins is used to'
            'sample data in external mux mode.'
            'Valid values for single external multiplexer mode are:'
            'Valid values for dual external multiplexer mode are:'
            ''
            'This property needs to be present if the device is configured for'
            'external multiplexer mode (either single or dual). If the device is'
            'not using external multiplexer mode the property is ignored.'),
        NodeDesc('xlnx,channels', None, False, desc=
                'List of external channels that are connected to the ADC', elements=[
            PropInt('#address-cells', required=True, 
                desc='Should be 1.'),
            PropInt('#size-cells', required=True, 
                desc='Should be 0.'),
            NodeDesc('None', None, False, desc=
                    'The child nodes of this node represent the external channels which are'
                    'connected to the ADC. If the property is no present no external'
                    'channels will be assumed to be connected.', elements=[
                NodeDesc('None', None, False, desc=
                        'Each child node represents one channel and has the following'
                        'properties:', elements=[
                    PropIntList('reg', required=True, valid_list='0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|16',
                        desc='Pair of pins the channel is connected to.'
                        'Note each channel number should only be used at most'
                        'once.'),
                    PropBool('xlnx,bipolar', 
                        desc='If set the channel is used in bipolar'
                        'mode.'),
                    ]),
                ]),
            ]),
        ]),
    ]
