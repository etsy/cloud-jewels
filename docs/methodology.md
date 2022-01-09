# Cloud Jewels Methodology

### Background

Sustainability has always been one of Etsy's core values. In 2017, Etsy set a goal of reducing the intensity of our energy use by 25% by 2025. In order to evaluate ourselves against this goal, we measure our energy usage in a lot of ways, including the energy consumption of our servers in our data centers. 

In 2018, we began a several-year-long process of migrating our technology infrastructure from our own physical hardware in data centers to Google Cloud Platform. This move will ultimately help towards our 25% goal because Google's data centers shares Etsy’s goal to power its operations with 100% renewable electricity and are much more efficient than the commercial data centers we currently use. Our old data centers have an average PUE (Power Usage Effectiveness) of 1.39 (FY18 average across colocated data centers), whereas Google's data centers have a combined average PUE of 1.11. PUE is a measure of how much energy the data center uses for things other than running the servers, such as cooling and backup power.

While a lower PUE helps our energy footprint significantly, we also want to be able to measure and optimize the amount of power that our servers draw. Knowing how much energy each of our servers uses helps us make design and code decisions that optimize for sustainability. We were able to do this when we had our own servers in a local data center, but this data is not currently available to us from Google. This paper is our attempt to estimate our energy consumption per service given only our billing data, resources we have found online, and the little we know about Google's infrastructure.

### Current Considerations and Limitations

After sharing this whitepaper with Arman Shehabi, a researcher in this field, we read a few more papers that he suggested might influence our estimates: "Comparing datasets of volume servers to illuminate their energy use in data centers", and "The Datacenter as a Computer: An Introduction to the Design of Warehouse-Scale Machines, Second Edition". While the comparative datasets paper suggests that servers frequently used in data centers are far less efficient than the idealistic claims made in the SPEC database, we know that Google uses custom-made servers that are likely maximally efficient. Additionally, we do not have a clear metric with which to adjust or scale our data to represent the difference, so we did not change our estimates based on that paper.

#### Networking

Google currently includes 2 Gbps internal networking "free" per vCPU. We know that requires a significant number of switches to power, and we are concerned that we are not currently capturing this power consumption because we are not being billed for it.

Additionally, the coefficient we have produced from our research for external networking, when applied to our data, appears to be far too high. We are considering alternative sources for determining the coefficient, and we are wondering whether perhaps we should halve or divide the amount of networking we are being billed for to account for only the "distance" of the networking that we are responsible for.

#### RAM

We do not yet have a coefficient to represent RAM. It is difficult to extract the power consumed by RAM from the power consumed by CPU. We have a paper that provides a graphical breakdown of percentage of power attributable to RAM vs CPU that in theory we could extract and apply to our CPU coefficient to estimate RAM, but since it is a graph without precise labels, and it varies with CPU utilization, we have not yet used this reference.

#### CPU Utilization

Our current coefficient does not take into account our own CPU utilization. It assumes an industry average across Google's servers. Applying our own average CPU utilization of the vCPUs that we use would possibly further increase the accuracy of our energy estimates.

#### On Confidence

As you may note: we are using point estimates without confidence intervals. This is partly intentional and highlights the experimental nature of this work. Our sources also provide single, rough estimates without confidence intervals, so we decided against numerically estimating our confidence so as to not provide false precision. Our work has been reviewed by several industry experts and assured by our auditors. Whenever there has been a choice, we have erred on the side of conservative estimates, taking responsibility for more energy consumption than we are likely responsible for to avoid overestimating our savings. Even though we have limited data, we are using these estimates as a jumping-off point and carrying forth in order to push ourselves and the industry forward. We especially welcome contributions and opinions. Let the conversation begin!

## Coefficient Estimates: Servers and Storage

As a rough starting point, we are estimating the wattage of an hour of virtual server use (vCPU) and a gigabyte-hour of drive storage. From some papers and the SPEC database (see References), we estimate the following:

- **2.1 Wh per vCPUh [Server]**
- **.89 Wh/TBh for HDD storage [Storage]**
- **1.52 Wh/TBh for SSD storage [Storage]**

In the below sections we will detail how we came to these numbers. 

### Coefficient Estimates Explained

#### Server Power Draw

If we know our average server utilization over a day, and the minimum and maximum wattage of our server at idle and 100% CPU usage, then we can calculate an average wattage for the server. We know that at idle, our server runs at its minimum wattage, so we start with that. Then we know that additional watts will be based on the CPU utilization, somewhere between our minimum wattage and our maximum wattage. This gives us the following equation:

**Wattage = Minimum wattage + Average CPU Utilization * (Maximum wattage - minimum wattage)**

In shorthand:

**W = Min + Util\*(Max - Min)**

### Application given what we know about Google's infrastructure

Google offers several options for its minimum CPU platform setting, all of which are Intel Xeon, likely 64 or 96 threads, and given that the approximate server lifetime is 4.4 years (page 7), we can filter the SPEC database to just look at only Intel Xeon servers made in 2015 and later. From those 73 reported servers of varying specs, we can get an average minimum and maximum wattage:

**Min: 50W**

**Max: 356W**

This is an estimated wattage for a google server, whereas when we spin up what is called a "compute instance" we are only using a fraction of a server. When we spin up a compute instance, we specify how many virtual CPUs (vCPUs) we need. If we consider a virtual CPU to be roughly equivalent to a server thread, we can again use the SPEC database to get our dynamic range and maximum wattage averages per thread. 

**Min: .55W**

**Max: 3.71W**

In the U.S. Data Center Energy Usage Report, the authors estimate that the average server utilization of servers in hyperscale data centers such as Google's was 45% in 2010 and will be 50% by 2020, so scaling that linearly (guessing) to 2019 gives us an estimated utilization of 49.5% for 2019.

Plugging these three estimates into our formula, we get an estimate of 2.11 W/vCPU:

**W = Min + Util\*(Max - Min)**

**W = .55 + .495(3.71 - .55) = 2.11**

#### Storage power draw

The authors of the U.S. Data Center Usage Report estimate that by 2020, HDDs will provide an average capacity of 10 TB/disk, and SSDs will provide an average capacity of 5 TB/disk. He also says the annual capacity growth rate for each is and will remain about 27%. (pages 14 and 15) Working backwards from 2020 to 2019, we get:

**HDD avg capacity = 10/1.27 = 7.87 TB/disk in 2019**

**SSD avg capacity = 5/1.27 = 3.94 TB/disk in 2019**

The average wattage per disk for HDDs was estimated to be 8.6 in 2015, and the data center paper authors estimate a 5% annual decrease in disk wattage to continue through 2020. Average wattage per disk for SDDs is assumed to be constant at 6W/drive, and is expected to remain so. (page 16)
Beginning with 8.6 in 2015, and reducing by 5% a year for 4 years, we get:

**HDD W/disk 2019 = 8.6\*(.95^4) = 7 W/disk**

**SSD W/disk 2019 = 6 W/disk**

If we combine these estimates, we can get an estimated wattage per TB:

**Watts per TB = Watts per disk / TBs per disk**

**HDD W/TB 2019 = 7 W / 7.87 TB = .89 W/TB**

**SSD W/TB 2019 = 6 W / 3.94 TB = 1.52 W/TB**

### References

Shehabi, A., Smith, S., Sartor, D., Brown, R., Herrlin, M., Koomey, J., Masanet, E., Horner, H., Azevedo, I., Lintner, W. (2016). *United States Data Center Energy Usage Report.* Ernest Orlando Lawrence Berkeley National Laboratory, Berkeley, California. LBNL-1005775. [https://eta.lbl.gov/sites/default/files/publications/lbnl-1005775_v2.pdf](https://eta.lbl.gov/sites/default/files/publications/lbnl-1005775_v2.pdf)

Aslan, J., Mayers, K., Koomey, J., France, C. "Electricity Intensity of Internet Data Transmission: Untangling the Estimates." *Journal of Industrial Ecology*, vol. 22, no. 4, Aug. 2017. [https://onlinelibrary.wiley.com/doi/pdf/10.1111/jiec.12630](https://onlinelibrary.wiley.com/doi/pdf/10.1111/jiec.12630)

SPEC (Standard Performance Evaluation Corporation) Power Results 2008 - 2019. [https://www.spec.org/power_ssj2008/results/power_ssj2008.html](https://www.spec.org/power_ssj2008/results/power_ssj2008.html)

Google Cloud Platform CPU Platforms [https://cloud.google.com/compute/docs/cpu-platforms](https://cloud.google.com/compute/docs/cpu-platforms)

Fuchs, H., Shehabi, A., Ganeshalingam, M., Desroches, L-B., Lim, B., Roth, K., Tsao, A. (2019). *Comparing datasets of volume servers to illuminate their energy use in data centers.* [https://doi.org/10.1007/s12053-019-09809-8](https://doi.org/10.1007/s12053-019-09809-8)

Barroso, L. A., Clidaras, J., Holzle, U. (2013). *The Datacenter as a Computer: An Introduction to the Design of Warehouse-Scale Machines, Second Edition.* Morgan & Claypool Publishers. [https://ai.google/research/pubs/pub41606](https://ai.google/research/pubs/pub41606)

### Additional calculations (for the extra curious)

#### Reverse derivation from US DC Usage Report formulae 

On page 12 of the US Data Center Energy Usage Report, the authors provide two equations that he uses to estimate power consumption:
	
**Slope of utilization vs power = Maximum server wattage x (1 - Dynamic Range)**

**Slope = Max\*(1 - DR)**

**Average server wattage = Maximum server wattage - slope of utilization vs power x (1 - average server utilization)**

**W = Max - Slope\*(1 - Util)**

We can work backwards from the equation we used for wattage to obtain these equations:

**W = Min + Util\*(Max - Min)**

First up, we'll convert our equation to use a term that the industry uses to compare how well servers scale their power with their CPU utilization called Dynamic Range (DR). Dynamic Range is defined as  the ratio of the minimum wattage of the server with idle CPU to the maximum wattage at 100% CPU utilization. An ideal server would idle at close to zero power, and its power consumption would scale proportionately with its CPU usage, so the ideal DR infinitely approaches zero. 

**Dynamic Range = Minimum wattage at idle CPU / Maximum wattage at 100% CPU**

If we want to consider dynamic range in our equation for average wattage, let's first multiply by 1 in the form of maximum wattage / maximum wattage (stick with me):
Our average server wattage formula from above:

**W = Min + Util\*(Max - Min)**

Expanded out into terms:

**W = Min + Util*Max - Util*Min**

Multiply by 1 in the form of Max/Max:

**W = Min\*Max/Max + Util\*Max\*Max/Max - Util\*Min\*Max/Max**

Since DR = Min/Max, we can substitute it in (and cancel out Max/Max in the middle term):

**W = DR*Max + Util*Max - Util*DR*Max**

Now we can factor out a Max to get a clean formula for average Wattage, given server utilization, Dynamic Range, and Maximum wattage.

**W = Max\*(DR + Util - Util\*DR)**

To get to the formulas from page 12 of the report, we have to take a few more steps, beginning with our formula as it looked before factoring out Max:

**W = DR\*Max + Util\*Max - Util\*DR\*Max**

First, multiply both sides by -1:

**-W  = -DR\*Max - Util\*Max + Util\*DR\*Max**

Then add Max to both sides:

**-W + Max = Max - DR\*Max - Util\*Max + Util\*DR\*Max**

Then we can factor (1 - Util) out of the right side:

**-W + Max = (Max - DR\*Max)(1 - Util)**

And further factor Max out of the first part:

**-W + Max = Max\*(1 - DR)(1 - Util)**

And switch sides to get everything positive again:

**W = Max - Max\*(1 - DR)(1 - Util)**

Now we can pull Max\*(1 - DR) out as our slope of utilization vs power (Equation 2, page 12 of the US DC paper):

**Slope = Max(1 - DR)**

Which leaves us with Equation 3, average server wattage:

**W = Max - Slope(1 - Util)**

#### Giving these equations numbers using US DC estimates

We can begin with the following estimates from the data center paper:

**Overall server average maximum wattage = 330W (page 9)**

This estimate is from 2007, but assumes that maximum server power will remain relatively constant through 2020 based on data from the SPEC database through 2015. This estimate also takes into account the estimated distribution of single (1S) vs multiple (2S+) socket servers.

**Average Dynamic Range = .44 (page 11)**

This estimate is from trends in the SPEC database through 2015, and is the estimate for 2020.

**Average Server Utilization = .495 (page 10)**

This is the estimated hyperscale volume server utilization estimate if scaled for 2019 (half a percentage point per year between 2010 and 2020).

Plugging these numbers into our equation, we get an estimated average wattage of :

**W = Max\*(DR + Util - Util\*DR)**

**W = 330\*(.44 + .495 - .44\*.495)** 

**W = 236.7**

