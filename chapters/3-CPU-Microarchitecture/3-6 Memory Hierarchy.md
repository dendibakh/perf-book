## Memory Hierarchy {#sec:MemHierar}

To effectively utilize all the hardware resources provisioned in the CPU, the machine needs to be fed with the right data at the right time. Understanding the memory hierarchy is critically important to deliver on the performance capabilities of a CPU. Most programs exhibit the property of locality; they don’t access all code or data uniformly. A CPU memory hierarchy is built on two fundamental properties:

* **Temporal locality**: when a given memory location is accessed, it is likely that the same location will be accessed again in the near future. Ideally, we want this information to be in the cache next time we need it.
* **Spatial locality**: when a given memory location is accessed, it is likely that nearby locations will be accessed in the near future. This refers to placing related data close to each other. When a program reads a single byte from memory, typically, a larger chunk of memory (cache line) is fetched because very often, the program will require that data soon.

This section provides a summary of the key attributes of memory hierarchy systems supported on modern CPUs.

### Cache Hierarchy

A cache is the first level of the memory hierarchy for any request (for code or data) issued from the CPU pipeline. Ideally, the pipeline performs best with an infinite cache with the smallest access latency. In reality, the access time for any cache increases as a function of the size. Therefore, the cache is organized as a hierarchy of small, fast storage blocks closest to the execution units, backed up by larger, slower blocks. A particular level of the cache hierarchy can be used exclusively for code (instruction cache, i-cache) or for data (data cache, d-cache), or shared between code and data (unified cache). Furthermore, some levels of the hierarchy can be private to a particular CPU, while other levels can be shared among CPUs. 

Caches are organized as blocks with a defined block size (**cache line**). The typical cache line size in modern CPUs is 64 bytes. Caches closest to the execution pipeline typically range in size from 8KiB to 32KiB. Caches further out in the hierarchy can be 64KiB to 16MiB in modern CPUs. The architecture for any level of a cache is defined by the following four attributes.

#### Placement of Data within the Cache. 

The address for a request is used to access the cache. In direct-mapped caches, a given block address can appear only in one location in the cache and is defined by a mapping function shown below. 
$$
\textrm{Number of Blocks in the Cache} = \frac{\textrm{Cache Size}}{\textrm{Cache Block Size}}
$$
$$
\textrm{Direct mapped location} = \textrm{(block address)  mod  (Number of Blocks in the Cache )}
$$

In a fully associative cache, a given block can be placed in any location in the cache. 

An intermediate option between the direct mapping and fully associative mapping is a set-associative mapping. In such a cache, the blocks are organized as sets, typically each set containing 2, 4, 8 or 16 blocks. A given address is first mapped to a set. Within a set, the address can be placed anywhere, among the blocks in that set. A cache with m blocks per set is described as an m-way set-associative cache. The formulas for a set-associative cache are:
$$
\textrm{Number of Sets in the Cache} = \frac{\textrm{Number of Blocks in the Cache}}{\textrm{Number of Blocks per Set (associativity)}}
$$
$$
\textrm{Set (m-way) associative location} = \textrm{(block address)  mod  (Number of Sets in the Cache)}
$$

#### Finding Data in the Cache.

Every block in the m-way set-associative cache has an address tag associated with it. In addition, the tag also contains state bits such as valid bits to indicate whether the data is valid. Tags can also contain additional bits to indicate access information, sharing information, etc. that will be described in later sections. 

![Address organization for cache lookup.](../../img/uarch/CacheLookup.png){#fig:CacheLookup width=80%}

Figure @fig:CacheLookup shows how the address generated from the pipeline is used to check the caches. The lowest order address bits define the offset within a given block; the block offset bits (5 bits for 32-byte cache lines, 6 bits for 64-byte cache lines). The set is selected using the index bits based on the formulas described above. Once the set is selected, the tag bits are used to compare against all the tags in that set. If one of the tags matches the tag of the incoming request and the valid bit is set, a cache hit results. The data associated with that block entry (read out of the data array of the cache in parallel to the tag lookup) is provided to the execution pipeline. A cache miss occurs in cases where the tag is not a match.

#### Managing Misses. 

When a cache miss occurs, the controller must select a block in the cache to be replaced to allocate the address that incurred the miss. For a direct-mapped cache, since the new address can be allocated only in a single location, the previous entry mapping to that location is deallocated, and the new entry is installed in its place. In a set-associative cache, since the new cache block can be placed in any of the blocks of the set, a replacement algorithm is required. The typical replacement algorithm used is the LRU (least recently used) policy, where the block that was least recently accessed is evicted to make room for the miss address. Another alternative is to randomly select one of the blocks as the victim block. Most CPUs define these capabilities in hardware, making it easier for executing software. 

#### Managing Writes. 

Read accesses to caches are the most common case as programs typically read instructions, and data reads are larger than data writes. Handling writes in caches is harder, and CPU implementations use various techniques to handle this complexity. Software developers should pay special attention to the various write caching flows supported by the hardware to ensure the best performance of their code.

CPU designs use two basic mechanisms to handle writes that hit in the cache:

* In a write-through cache, hit data is written to both the block in the cache and to the next lower level of the hierarchy.
* In a write-back cache, hit data is only written to the cache. Subsequently, lower levels of the hierarchy contain stale data. The state of the modified line is tracked through a dirty bit in the tag. When a modified cache line is eventually evicted from the cache, a write-back operation forces the data to be written back to the next lower level.  

Cache misses on write operations can be handled in two ways:

* In a *write-allocate or fetch on write miss* cache, the data for the missed location is loaded into the cache from the lower level of the hierarchy, and the write operation is subsequently handled like a write hit.
* If the cache uses a *no-write-allocate policy*, the cache miss transaction is sent directly to the lower levels of the hierarchy, and the block is not loaded into the cache. 

Out of these options, most designs typically choose to implement a write-back cache with a write-allocate policy as both of these techniques try to convert subsequent write transactions into cache-hits, without additional traffic to the lower levels of the hierarchy. Write through caches typically use the no-write-allocate policy.

#### Other Cache Optimization Techniques. 

For a programmer, understanding the behavior of the cache hierarchy is critical to extract performance from any application. This is especially true when CPU clock frequencies increase while the memory technology speeds lag behind. From the perspective of the pipeline, the latency to access any request is given by the following formula that can be applied recursively to all the levels of the cache hierarchy up to the main memory: 
$$
\textrm{Average Access Latency} = \textrm{Hit Time } + \textrm{ Miss Rate } \times \textrm{ Miss Penalty}
$$
Hardware designers take on the challenge of reducing the hit time and miss penalty through many novel micro-architecture techniques. Fundamentally, cache misses stall the pipeline and hurt performance. The miss rate for any cache is highly dependent on the cache architecture (block size, associativity) and the software running on the machine. As a result, optimizing the miss rate becomes a hardware-software co-design effort. As described in the previous sections, CPUs provide optimal hardware organization for the caches. Additional techniques that can be implemented both in hardware and software to minimize cache miss rates are described below.

[TODO]: Memory renaming?

##### HW and SW Prefetching. {#sec:HwPrefetch}

One method to reduce a cache miss and the subsequent stall is to prefetch instructions as well as data into different levels of the cache hierarchy prior to when the pipeline demands. The assumption is the time to handle the miss penalty can be mostly hidden if the prefetch request is issued sufficiently ahead in the pipeline. Most CPUs support implicit hardware-based prefetching that is complemented by explicit software prefetching that programmers can control. 

Hardware prefetchers observe the behavior of a running application and initiate prefetching on repetitive patterns of cache misses. Hardware prefetching can automatically adapt to the dynamic behavior of the application, such as varying data sets, and does not require support from an optimizing compiler or profiling support. Also, the hardware prefetching works without the overhead of additional address-generation and prefetch instructions. However, hardware prefetching is limited to learning and prefetching for a limited set of cache-miss patterns that are implemented in hardware.

Software memory prefetching complements the one done by the HW. Developers can specify which memory locations are needed ahead of time via dedicated HW instruction (see [@sec:memPrefetch]). Compilers can also automatically add prefetch instructions into the code to request data before it is required. Prefetch techniques need to balance between demand and prefetch requests to guard against prefetch traffic slowing down demand traffic. 

### Main Memory

Main memory is the next level of the hierarchy, downstream from the caches. Requests to load and store data are initiated by the Memory Controller Unit (MCU). In the past, this circuit was located inside the motherboard chipset, in the north bridge chip. But nowadays, most processors have this component embedded, so the CPU has a dedicated memory bus connecting it to the main memory.

Main memory uses DRAM (Dynamic Random Access Memory), technology that supports large capacities at reasonable cost points. When comparing DRAM modules, people usually look at memory density and memory speed, besides its price, of course. Memory density defines how much memory the module has, measured in GB. Obviously the more available memory the better as it is a precious resource used by the OS and applications.

Performance of main memory is described by latency and bandwidth. Memory latency is the time elapsed between the memory access request is issued and when the data is available to use by CPU. Memory bandwidth defines how many bytes can be fetch per some period of time, usually measured in gigabytes per second.

#### DDR

DDR (Double Data Rate) DRAM technology is the predominant DRAM technology supported by most CPUs. Historically, DRAM bandwidths have improved every generation while the DRAM latencies have stayed the same or even increased. Table @tbl:mem_rate shows the top data rate, peak bandwidth, and the corresponding reading latency for the last three generations of DDR technologies. The data rate is measured as a million transfers per sec (MT/s). The latencies shown in this table correspond to the latency in the DRAM device itself. Typically, the latencies as seen from the CPU pipeline (cache miss on a load to use) are higher (in the 50ns-150ns range) due to additional latencies and queuing delays incurred in the cache controllers, memory controllers, and on-die interconnects. See an example of measuring observed memory latency and bandiwdth in [@sec:MemLatBw].

-----------------------------------------------------------------
   DDR       Year   Highest Data   Peak Bandwidth  In-device Read
Generation           Rate(MT/s)     (Gbytes/s)      Latency(ns)
----------  ------  ------------   --------------  --------------
  DDR3       2007      2133            12.8            10.3

  DDR4       2014      3200            25.6            12.5

  DDR5       2020      6400            51.2            14

-----------------------------------------------------------------

Table: Performance characteristics for the last three generations of DDR technologies. {#tbl:mem_rate}

It is worth to mention that DRAM chips require memory cells being periodically refreshed. Because the bit value is stored as the presence of an electric charge on a tiny capacitor, it can lose its charge as the time passes. To prevent this, there is a special circuitry that reads each cell and writes it back, effectively restoring the capacitor's charge. While a DRAM chip is in its refresh procedure, it is not serving memory access requests.

DRAM module is organized as sets of DRAM chips. Memory *rank* is a term that describes how many sets of DRAM chips exist on a module. For example, a single-rank (1R) memory module contains one set of DRAM chips. A dual-rank (2R) memory module has two sets of DRAM chips, therefore doubling the capacity of a single-rank module. Likewise, there are quad-rank (4R) and octa-rank (8R) memory modules available for purchase.

Each rank consists of multiple DRAM chips. Memory *width* defines how wide the bus of each DRAM chip is. And since each rank is 64-bits wide (or 72-bits wide for ECC RAM), it also defines the number of DRAM chips present within the rank. Memory width can be one of three values: `x4`, `x8` or `x16`, which define how wide is the bus that goes to each chip. As an example, Figure @fig:Dram_ranks shows the organization of 2Rx16 dual-rank DRAM DDR4 module, total 2GB capacity. There are four chips in each rank, with a 16-bit wide bus. Combined, the four chips provide 64-bit output. The two ranks are selected one at a time through a rank select signal.

![Organization of 2Rx16 dual-rank DRAM DDR4 module, total 2GB capacity.](../../img/uarch/DRAM_ranks.png){#fig:Dram_ranks width=80%}

There is no direct answer whether performance of single-rank or dual-rank is better as it depends on the type of application. Switching from one rank to another through rank select signal needs additional clock cycles, which may increase the access latency. On the other hand, if a rank is not accessed, it can go through its refresh cycles in parallel while other ranks are busy. As soon as the previous rank completes data transmission, the next rank can immediately start its transmission. Also, single-rank modules produce less heat and are less likely to fail.

Going further, we can install multiple DRAM modules in a system to not only increase memory capacity, but also memory bandwidth. Setups with multiple memory channels are used to scale up the communication speed between the memory controller and the DRAM.

A system with a single memory channel has a 64-bit wide data bus between the DRAM and memory controller. The multi-channel architectures increase the width of the memory bus, allowing DRAM modules to be accessed simultaneously. For example, the dual-channel architecture expands the width of the memory data bus from 64 bit to 128 bit, doubling the available bandwidth, see Figure @fig:Dram_channels. Notice, that each memory module, is still a 64-bit device, but we connect them differently. It is very typical nowadays for server machines to have four and eight memory channels. 

![Organization of a dual-channel DRAM setup.](../../img/uarch/DRAM_channels.png){#fig:Dram_channels width=50%}

Alternatively, you could also encounter setups with duplicated memory controllers. For example, a processor may have two integrated memory controllers, each of them capable of supporting several memory channels. The two controllers are independent and only view their own slice of the total physical memory address space.

We can do a quick calculations to determine the maximum memory bandwidth for a given memory technology, using a simple formula below:
$$
\textrm{Max. Memory Bandwidth} = \textrm{Data Rate } \times \textrm{ Bytes per cycle }
$$

For example, for a single-channel DDR4 configuration, the data rate is `2400 MT/s` and 64 bits or 8 bytes can be transfered each memory cycle, thus the maximum bandiwdth equals to `2400 * 8 = 19.2 GB/s`. Dual-channel or dual memory controller setups double the bandwidth to `38.4 GB/s`. Remember though, that those numbers are theoretical maximums, that assume that a data transfer will occur at each memory clock cycle, which in fact never happens in practice. So, when measuring actual memory speed, you will always see a value lower than the maximum theoretical transfer bandwidth. 

To enable multi-channel configuration, you need to have a CPU and a motherboard that supports such architecture and install an even number of identical memory modules in the correct memory slots on the motherboard. The quickest way to check the setup on Windows is by running a hardware identification utility like `CPU-Z` or `HwInfo`, on Linux one can use `dmidecode` command. But also, you can run memory bandwidth benchmarks like Intel `mlc` or `Stream`.

To make use of multiple memory channels in a system, there is a technique called interleaving. It spreads adjacent addresses within a page across multiple memory devices. Example of a 2-way interleaving for sequential memory accesses is shown in Figure @fig:Dram_channel_interleaving. As before, we have dual-channel memory configuration (channels A and B) with two independent memory controllers. Modern processors interleave per four cache lines (256 bytes), i.e. first four adjacent cache lines go to the channel A, and then the next set of four cache lines go to the channel B.

![2-way interleaving for sequential memory access.](../../img/uarch/DRAM_channel_interleaving.png){#fig:Dram_channel_interleaving width=70%}

Without interleaving, consecutive adjacent accesses would be sent to the same memory controller, not utilizing the second available controller. While using the technique increases hardware-level parallelism and allows to effectively utilize all available bandwidth from the memory devices in a setup. For most workloads, performance is maximized when all the channels are populated as it spreads a single memory region across as many DRAM modules as possible.

While increased memory bandwidth is generally good, it does not always translate into better system performance and is highly dependent on the application. On the other hand, it's important to watch out for available and utilized memory bandwidth, because once it becomes the primary bottleneck, the application stops scaling, i.e. adding more cores doesn't make it run faster.

#### GDDR and HBM

Besides multi-channel DDR, there are other technologies that target workloads where higher memory bandwidth is required to achieve greater performance. Technologies such as GDDR (Graphics DDR) and HBM (High Bandwidth Memory) are the most notable ones. They find their use in high-end graphics, high-performance computing such as climate modeling, molecular dynamics, physics simulation, but also in autonomous driving, and of course, AI/ML. They are a natural fit there because such applications require moving large amounts of data very quickly.

GDDR was primary designed for graphics and nowadays it is used on virtually every high-performance graphics card. While GDDR shares some charasteristics with DDR, it is also quite different. While DRAM DDR is designed for lower latencies, GDDR is built for much higher bandwidth, because it is located in the same package as the processor chip itself. Similar to DDR, the GDDR interface transfers two 32 bit (64-bit total) wide data words per clock cycle. The latest GDDR6X standard can achieve up to 168 GB/s bandwidth, operating at a relatively low 656 MHz frequency.

HBM is a new type of CPU/GPU memory that vertically stacks memory chips, also called 3D stacking. Similar to GDDR, HBM drastically shortens the distance data needs to travel to reach a processor. The main difference from DDR and GDDR, is that HBM memory bus is very wide: 1024 bits per each HBM stacks. It allows HBM to achieve ultra-high bandwidth. The latest HBM3 standard supports up to 665 GB/s bandwidth per package. It also operates at a low frequency of 500 Mhz and has a memory density of up to 48 GB per package.

A system with HBM onboard will be a good choice if you're looking to get as much memory bandwidth as you can get. However, at the time of writing, this technology is quite expensive. As GDDR is predominantly used in graphics cards, HBM may be a good option to accelerate certain workloads that run on CPU. In fact, we start seeing first x86 general purpose server chips with integrated HBM.