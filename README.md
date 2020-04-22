# Cloud Jewels: Estimating Energy Consumption on GCP

This repo illustrates how to estimate GCP energy consumption using data from the
[GCP Billing
export](https://cloud.google.com/billing/docs/how-to/export-data-bigquery) in
BigQuery. The script provided scans all resource usage over a trailing thirty
day period and estimates consumption by using a hard-coded coefficient lookup
table. 

## Usage

To run the script, modify the [usage_by_jewel_class.sql](https://github.etsycorp.com/Engineering/cloud-jewels/blob/master/sql/usage_by_jewel_class.sql#L41) file to point to your
billing export table in BigQuery. Also be sure you have the [Cloud SDK: Command
Line Interface](https://cloud.google.com/sdk) installed. Once you do, run the
script shown below and you should see a similar output table representing your
estimated trailing thirty day consumption estimates!

```bash
> ./cloud-jewels.sh -p my-billing-project
>
> Waiting on bqjob_r2a1f3145ee30850a_000001711743b581_1 ... (1s) Current status:
> DONE

+------------------+------+--------------------+
|   jewel_class    | skus |    cloud_jewels    |
+------------------+------+--------------------+
| CPU              |   17 |          xxxxxx.xx |
| Cloud Storage    |   25 |            xxxx.xx |
| Storage          |   16 |            xxxx.xx |
| SSD Storage      |    4 |              xx.xx | 
| GPU              |    4 |               x.xx |
| Excluded Service |  281 |                0.0 |
| Network          |   36 |                0.0 |
| Memory           |   13 |                0.0 |
+------------------+------+--------------------+
```

## Reference

* [Blog Post](https://codeascraft.com/)
