################################################################################
# Collectl:   V3.6.9-1  HiRes: 1  Options: -sCXNZ -i1:1 --procfilt=cmama -P -f /home/mmulhern/CHECK_PARSING/OpenMAMA-bfbeefe/sample_data/sample -oUm 
# Host:       ibm02  DaemonOpts: 
# Booted:     1387366662.66 [20131218-11:37:42]
# Distro:     Red Hat Enterprise Linux Server release 6.2 (Santiago)  Platform: 
# Date:       20140327-131445  Secs: 1395926085 TZ: +0000
# SubSys:     CXNZ Options: Um Interval: 1:1 NumCPUs: 12  NumBud: 0 Flags: ix
# Filters:    NfsFilt:  EnvFilt:  TcpFilt: ituc
# HZ:         100  Arch: x86_64-linux-thread-multi PageSize: 4096
# Cpu:        GenuineIntel Speed(MHz): 3333.459 Cores: 6  Siblings: 6 Nodes: 2
# Kernel:     2.6.32-220.el6.x86_64  Memory: 24561944 kB  Swap: 26804216 kB
# NumDisks:   4 DiskNames: sda dm-0 dm-1 dm-2
# NumNets:    10 NetNames: lo:?? usb0:?? eth2:1000 eth3:?? eth0:?? eth1:?? eth6:?? eth7:?? eth10:10000 ib0:??
# IConnect:   NumHCAs: 2 PortStates: 11:11 IBVersion: 1.5.3-3.1.0): PQVersion: 1.5.8
# SCSI:       DA:0:02:00:00 CD:1:00:00:00
################################################################################
#UTC PID User PR PPID THRD S VmSize VmLck VmRSS VmData VmStk VmExe VmLib CPU SysT UsrT PCT AccumT RKB WKB RKBC WKBC RSYS WSYS CNCL MajF MinF Command
1395926098.001 15921 503 20 11506 0 R 186100 0 17852 131372 88 40 7072 0 0.01 0.40 41 00:00.41 196 4 57 0 54 11 0 2 4635 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926099.001 15921 503 20 11506 0 R 186100 0 17852 131372 88 40 7072 0 0.00 1.00 100 00:01.41 0 0 0 0 0 1 0 0 0 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926100.001 15921 503 20 11506 0 R 188264 0 20048 133536 88 40 7072 0 0.12 0.88 100 00:02.41 0 0 630 0 164 1 0 0 554 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926100.001 15943 503 20 12717 0 S 313352 0 20968 258608 88 52 7072 7 0.08 0.44 52 00:00.52 0 4 687 0 218 9 0 0 4911 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926101.001 15921 503 20 11506 0 R 190056 0 21796 135328 88 40 7072 0 0.12 0.88 100 00:03.41 0 0 0 0 0 1 0 0 437 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926101.001 15943 503 20 12717 0 S 313484 0 20980 258740 88 52 7072 7 0.11 0.51 62 00:01.14 0 0 0 0 0 1 0 0 3 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926102.001 15921 503 20 11506 0 R 193640 0 24988 138912 88 40 7072 0 0.13 0.88 101 00:04.42 0 0 0 0 0 1 0 0 287 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926102.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.09 0.50 59 00:01.73 0 0 0 0 0 1 0 0 49 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926103.001 15921 503 20 11506 0 R 193640 0 25320 138912 88 40 7072 0 0.15 0.85 100 00:05.42 0 0 0 0 0 1 0 0 82 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926103.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.10 0.54 64 00:02.37 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926104.001 15921 503 20 11506 0 R 200808 0 29088 146080 88 40 7072 0 0.13 0.86 99 00:06.41 0 0 0 0 0 1 0 0 432 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926104.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.07 0.40 47 00:02.84 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926105.001 15921 503 20 11506 0 R 200808 0 29088 146080 88 40 7072 0 0.12 0.89 101 00:07.42 0 0 0 0 0 1 0 0 0 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926105.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.05 0.38 43 00:03.27 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926106.001 15921 503 20 11506 0 S 200808 0 31136 146080 88 40 7072 0 0.13 0.87 100 00:08.42 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926106.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.09 0.41 50 00:03.77 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926107.001 15921 503 20 11506 0 R 200808 0 32336 146080 88 40 7072 0 0.12 0.87 99 00:09.41 0 0 0 0 0 1 0 0 300 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926107.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.07 0.34 41 00:04.18 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926108.001 15921 503 20 11506 0 R 215144 0 35236 160416 88 40 7072 0 0.14 0.86 100 00:10.41 0 0 0 0 0 1 0 0 214 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926108.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.07 0.44 51 00:04.69 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926109.001 15921 503 20 11506 0 R 215144 0 37284 160416 88 40 7072 0 0.13 0.88 101 00:11.42 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926109.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.07 0.42 49 00:05.18 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926110.001 15921 503 20 11506 0 R 215144 0 39332 160416 88 40 7072 0 0.13 0.86 99 00:12.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926110.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.06 0.35 41 00:05.59 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926111.001 15921 503 20 11506 0 R 215144 0 41380 160416 88 40 7072 0 0.13 0.87 100 00:13.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926111.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.07 0.43 50 00:06.09 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926112.001 15921 503 20 11506 0 R 280680 0 41384 225952 88 40 7072 0 0.14 0.86 100 00:14.41 0 0 0 0 2 2 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926112.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.08 0.44 52 00:06.61 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926113.001 15921 503 20 11506 0 R 280680 0 43432 225952 88 40 7072 0 0.14 0.86 100 00:15.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926113.001 15943 503 20 12717 0 S 313484 0 21176 258740 88 52 7072 7 0.07 0.41 48 00:07.09 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926114.001 15921 503 20 11506 0 R 280680 0 45480 225952 88 40 7072 0 0.14 0.86 100 00:16.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926114.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.08 0.41 49 00:07.57 0 0 0 0 2 2 0 0 1 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926115.001 15921 503 20 11506 0 R 280680 0 46448 225952 88 40 7072 0 0.12 0.88 100 00:17.41 0 0 0 0 0 1 0 0 242 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926115.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.06 0.39 45 00:08.03 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926116.001 15921 503 20 11506 0 R 309352 0 49304 254624 88 40 7072 0 0.14 0.86 100 00:18.41 0 0 0 0 0 1 0 0 203 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926116.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.07 0.36 43 00:08.46 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926117.001 15921 503 20 11506 0 R 309352 0 51352 254624 88 40 7072 0 0.14 0.87 101 00:19.42 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926117.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.07 0.43 50 00:08.96 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926118.001 15921 503 20 11506 0 R 309352 0 53400 254624 88 40 7072 0 0.12 0.87 99 00:20.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926118.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.08 0.38 46 00:09.42 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926119.001 15921 503 20 11506 0 R 309352 0 55448 254624 88 40 7072 0 0.13 0.87 100 00:21.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926119.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.08 0.38 46 00:09.88 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926120.001 15921 503 20 11506 0 R 309352 0 55448 254624 88 40 7072 0 0.13 0.87 100 00:22.41 0 0 0 0 0 1 0 0 0 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926120.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.08 0.37 45 00:10.33 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926121.001 15921 503 20 11506 0 R 309352 0 57496 254624 88 40 7072 0 0.12 0.88 100 00:23.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926121.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.09 0.42 51 00:10.84 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926122.001 15921 503 20 11506 0 R 309352 0 59544 254624 88 40 7072 0 0.13 0.87 100 00:24.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926122.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.06 0.45 51 00:11.35 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926123.001 15921 503 20 11506 0 R 309352 0 61592 254624 88 40 7072 0 0.13 0.87 100 00:25.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926123.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.10 0.41 51 00:11.86 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926124.001 15921 503 20 11506 0 R 309352 0 63640 254624 88 40 7072 0 0.14 0.86 100 00:26.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926124.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.07 0.43 50 00:12.36 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926125.001 15921 503 20 11506 0 R 309352 0 65688 254624 88 40 7072 0 0.14 0.86 100 00:27.41 0 0 0 0 0 1 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926125.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.07 0.45 52 00:12.88 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926126.001 15921 503 20 11506 0 R 309352 0 67736 254624 88 40 7072 0 0.13 0.87 100 00:28.41 0 0 0 0 2 2 0 0 1 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926126.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.07 0.37 44 00:13.32 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926127.001 15921 503 20 11506 0 R 309352 0 67736 254624 88 40 7072 0 0.13 0.87 100 00:29.41 0 0 0 0 0 1 0 0 0 ./bin/mamaproducerc_v2 -m qpid -tport pub -S MAMA -s sym
1395926127.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.05 0.44 49 00:13.81 0 0 0 0 0 1 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926128.001 15943 503 20 12717 0 S 379020 0 21180 324276 88 52 7072 7 0.01 0.06 7 00:13.88 0 0 0 0 2 2 0 0 0 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
1395926129.001 15943 503 20 12717 0 S 379020 0 19168 324276 88 52 7072 7 0.20 1.11 131 00:15.19 0 0 0 0 0 3 0 0 3 ./bin/mamaconsumerc_v2 -m qpid -tport sub -S MAMA -s sym
