# List of the Major CPU Microarchitectures {.unnumbered}

\markright{List of the Major CPU Microarchitectures}

In the tables below we present the most recent ISAs and microarchitectures from Intel, AMD, and ARM-based vendors. Of course, not all the designs are listed here. We only include those that we reference in the book or if they represent a big transition in the evolution of the platform.

---------------------------------------------------------------
    Name       Three-letter     Year released    Supported ISA
                 acronym                         client/server
                                                     chips
------------  ---------------  ---------------  ---------------
   Nehalem         NHM              2008             SSE4.2

Sandy Bridge       SNB              2011              AVX

   Haswell         HSW              2013              AVX2

   Skylake         SKL              2015         AVX2 / AVX512

 Sunny Cove        SNC              2019             AVX512

 Golden Cove       GLC              2021         AVX2 / AVX512 

Redwood Cove       RWC              2023         AVX2 / AVX512 

---------------------------------------------------------------

Table: List of the most recent Intel Core microarchitectures. {#tbl:IntelUarchs}

----------------------------------------------
    Name       Year released    Supported ISA
------------  ---------------  ---------------
Streamroller       2014              AVX

  Excavator        2015              AVX2

   Zen             2017              AVX2

   Zen2            2019              AVX2

   Zen3            2020              AVX2

   Zen4            2022             AVX512

----------------------------------------------

Table: List of the most recent AMD microarchitectures. {#tbl:AMDUarchs}

------------------------------------------------------------------
    ISA        Year released     ARM uarchs         Third-party
                                  (latest)            uarchs
------------  ---------------  --------------   ------------------
  ARMv7-A          2005          Cortex-A17          Apple A6;
  (32bit)                                       Quallcomm Scorpion

  ARMv8-A          2011          Cortex-A73        Apple A7-A10;
                                                  Quallcomm Kryo;
                                                 Samsung M1/M2/M3

 ARMv8.2-A         2016         Neoverse N1;         Apple A11;
                                 Cortex-X1           Samsung M4;
                                                    Ampere Altra

 ARMv8.4-A         2017         Neoverse V1        AWS Graviton3;
                                                   Apple A13, M1

 ARMv9.0-A         2018         Neoverse V2;        NVIDIA Grace
(64bit-only)                    Neoverse N2;
                                 Cortex X3

 ARMv8.6-A         2019             ---           Apple A15,A16,M2
(64bit-only)

 ARMv9.2-A         2020          Cortex X4              ---

 ARMv9.4-A         2022             ---                 ---
------------------------------------------------------------------

Table: List of ARM ISAs along with their own and third-party implementations. {#tbl:ARMUarchs}

\bibliography{biblio}