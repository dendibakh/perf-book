\phantomsection
# List of the Major CPU Microarchitectures {.unnumbered}

\markboth{List of the Major CPU Microarchitectures}{List of the Major CPU Microarchitectures}

In the tables below we present the most recent ISAs and microarchitectures from Intel, AMD, and ARM-based vendors. Of course, not all the designs are listed here. We only include those that we reference in the book or if they represent a big transition in the evolution of the platform.

-----------------------------------------------------------------
    Name         Three-letter     Year released     Supported ISA
                  acronym                          client/server
                                                       chips
--------------  ---------------  ---------------  ---------------
   Nehalem           NHM              2008             SSE4.2

Sandy Bridge         SNB              2011              AVX

   Haswell           HSW              2013              AVX2

   Skylake           SKL              2015         AVX2 / AVX512

 Sunny Cove          SNC              2019             AVX512

 Golden Cove         GLC              2021         AVX2 / AVX512 

 Redwood Cove        RWC              2023         AVX2 / AVX512 

  Lion Cove          LNC              2024             AVX2

-----------------------------------------------------------------

Table: List of the recent Intel Core microarchitectures. {#tbl:IntelUarchs}

----------------------------------------------
    Name       Year released    Supported ISA
------------  ---------------  ---------------
Streamroller       2014              AVX

  Excavator        2015              AVX2

   Zen             2017              AVX2

   Zen2            2019              AVX2

   Zen3            2020              AVX2

   Zen4            2022             AVX512

   Zen5            2024             AVX512

----------------------------------------------

Table: List of the recent AMD microarchitectures. {#tbl:AMDUarchs}

\newpage

------------------------------------------------------------------
    ISA        Year of ISA      ARM uarchs         Third-party
                 release         (latest)            uarchs
------------  ---------------  --------------   ------------------
  ARMv8-A          2011          Cortex-A73        Apple A7-A10;
                                                  Qualcomm Kryo;
                                                 Samsung M1/M2/M3

 ARMv8.2-A         2016         Neoverse N1;         Apple A11;
                                 Cortex-X1           Samsung M4;
                                                    Ampere Altra

 ARMv8.4-A         2017         Neoverse V1        AWS Graviton3;
                                                   Apple A13, M1

 ARMv9.0-A         2018         Neoverse N2;    Microsoft Cobalt 100;
(64bit-only)                    Neoverse V2;        NVIDIA Grace;
                                 Cortex X3          AWS Graviton4;

 ARMv8.6-A         2019             ---          Apple A15, A16, M2, M3
(64bit-only)

 ARMv9.2-A         2020          Cortex X4             Apple M4
------------------------------------------------------------------

Table: List of recent ARM ISAs along with their own and third-party implementations. {#tbl:ARMUarchs}

\bibliography{biblio}