<!-- README.md is generated from README.Rmd. Please edit that file -->
A lot of customers ask what are a few good things to try while the `Hadoop` vendor is still around demonstrating the new `Spark` cluster (itself often a "proof of concept" or POC cluster).

My currents answer is: load and view a few big files and also try to break the cluster to get the cleanup and recovery procedures while you are not in a panic.

For the "big file" test I suggest having a large file in Hadoop and insisting on seeing something like `spark_write_parquet()` run on it and examing the top of the file through the `head()` command.

For breaking the cluster, I suggest asking the vendor if they are willing to experiment with you on this and not trying this on any cluster you don't intend to re-format.

Let's break a practice cluster. Do not try this on a `Spark` cluster you are not willing to dispose of. We are setting this to be a `local` cluster which is a transient cluster `Sparklyr` builds for us. This transient cluster will go away when we shut down `RStudio`.

``` r
library("sparklyr")
packageVersion('sparklyr')
```

    ## [1] '0.5.4'

``` r
library("dplyr")
```

    ## 
    ## Attaching package: 'dplyr'

    ## The following objects are masked from 'package:stats':
    ## 
    ##     filter, lag

    ## The following objects are masked from 'package:base':
    ## 
    ##     intersect, setdiff, setequal, union

``` r
packageVersion('dplyr')
```

    ## [1] '0.5.0'

``` r
# Please see the following video for installation help
#  https://youtu.be/qnINvPqcRvE
# spark_install(version = "2.1.0")

# set up a local "practice" Spark instance
sc <- spark_connect(master = "local",
                    version = "2.1.0")
#print(sc)
```

The following code (which is just one typo away from correct code, typo marked) ruins the transient cluster. Not only does it throw an error but at the very least the connection to the cluster (in this case a temporary local cluster) is damaged (at least with version `1.0.136` , `Sparklyr 0.5.4`, and `dplyr 0.5.0`; all current as of 4-29-2017).

After executing this the refresh "swirl" in the RStudio Spark environment browser throws a pop-up saying "Error: R code execution error" and the console reports the error "Error: Variables must be length 1 or 1. Problem variables: 'database'".

``` r
# build notional data, but do not
# leave it in the system (so we can
# demonstrate loading).
names <- vapply(1:3,
                function(i) {
                  di <- data.frame(x=runif(10))
                  ni <- paste('data', sprintf("%02d", i), sep='_')
                  hi <- copy_to(sc, di, 
                                name= , # Typo error: left out ni,
                                overwrite= TRUE)
                  #spark_write_parquet(hi, path= ni)
                  dplyr::db_drop_table(sc, ni)
                  ni
                },
                character(1))
```

    ## Error: org.apache.spark.sql.catalyst.analysis.NoSuchTableException: Table or view 'data_01' not found in database 'default';
    ##  at org.apache.spark.sql.catalyst.catalog.SessionCatalog.dropTable(SessionCatalog.scala:539)
    ##  at org.apache.spark.sql.execution.command.DropTableCommand.run(ddl.scala:209)
    ##  at org.apache.spark.sql.execution.command.ExecutedCommandExec.sideEffectResult$lzycompute(commands.scala:58)
    ##  at org.apache.spark.sql.execution.command.ExecutedCommandExec.sideEffectResult(commands.scala:56)
    ##  at org.apache.spark.sql.execution.command.ExecutedCommandExec.doExecute(commands.scala:74)
    ##  at org.apache.spark.sql.execution.SparkPlan$$anonfun$execute$1.apply(SparkPlan.scala:114)
    ##  at org.apache.spark.sql.execution.SparkPlan$$anonfun$execute$1.apply(SparkPlan.scala:114)
    ##  at org.apache.spark.sql.execution.SparkPlan$$anonfun$executeQuery$1.apply(SparkPlan.scala:135)
    ##  at org.apache.spark.rdd.RDDOperationScope$.withScope(RDDOperationScope.scala:151)
    ##  at org.apache.spark.sql.execution.SparkPlan.executeQuery(SparkPlan.scala:132)
    ##  at org.apache.spark.sql.execution.SparkPlan.execute(SparkPlan.scala:113)
    ##  at org.apache.spark.sql.execution.QueryExecution.toRdd$lzycompute(QueryExecution.scala:87)
    ##  at org.apache.spark.sql.execution.QueryExecution.toRdd(QueryExecution.scala:87)
    ##  at org.apache.spark.sql.Dataset.<init>(Dataset.scala:185)
    ##  at org.apache.spark.sql.Dataset$.ofRows(Dataset.scala:64)
    ##  at org.apache.spark.sql.SparkSession.sql(SparkSession.scala:592)
    ##  at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
    ##  at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
    ##  at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
    ##  at java.lang.reflect.Method.invoke(Method.java:497)
    ##  at sparklyr.Invoke$.invoke(invoke.scala:94)
    ##  at sparklyr.StreamHandler$.handleMethodCall(stream.scala:89)
    ##  at sparklyr.StreamHandler$.read(stream.scala:55)
    ##  at sparklyr.BackendHandler.channelRead0(handler.scala:49)
    ##  at sparklyr.BackendHandler.channelRead0(handler.scala:14)
    ##  at io.netty.channel.SimpleChannelInboundHandler.channelRead(SimpleChannelInboundHandler.java:105)
    ##  at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:367)
    ##  at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:353)
    ##  at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:346)
    ##  at io.netty.handler.codec.MessageToMessageDecoder.channelRead(MessageToMessageDecoder.java:102)
    ##  at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:367)
    ##  at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:353)
    ##  at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:346)
    ##  at io.netty.handler.codec.ByteToMessageDecoder.fireChannelRead(ByteToMessageDecoder.java:293)
    ##  at io.netty.handler.codec.ByteToMessageDecoder.channelRead(ByteToMessageDecoder.java:267)
    ##  at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:367)
    ##  at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:353)
    ##  at io.netty.channel.AbstractChannelHandlerContext.fireChannelRead(AbstractChannelHandlerContext.java:346)
    ##  at io.netty.channel.DefaultChannelPipeline$HeadContext.channelRead(DefaultChannelPipeline.java:1294)
    ##  at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:367)
    ##  at io.netty.channel.AbstractChannelHandlerContext.invokeChannelRead(AbstractChannelHandlerContext.java:353)
    ##  at io.netty.channel.DefaultChannelPipeline.fireChannelRead(DefaultChannelPipeline.java:911)
    ##  at io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read(AbstractNioByteChannel.java:131)
    ##  at io.netty.channel.nio.NioEventLoop.processSelectedKey(NioEventLoop.java:652)
    ##  at io.netty.channel.nio.NioEventLoop.processSelectedKeysOptimized(NioEventLoop.java:575)
    ##  at io.netty.channel.nio.NioEventLoop.processSelectedKeys(NioEventLoop.java:489)
    ##  at io.netty.channel.nio.NioEventLoop.run(NioEventLoop.java:451)
    ##  at io.netty.util.concurrent.SingleThreadEventExecutor$2.run(SingleThreadEventExecutor.java:140)
    ##  at io.netty.util.concurrent.DefaultThreadFactory$DefaultRunnableDecorator.run(DefaultThreadFactory.java:144)
    ##  at java.lang.Thread.run(Thread.java:745)

The connection or cluster seems to be damaged.

``` r
DBI::dbListTables(sc)
```

    ## Error: Variables must be length 1 or 1.
    ## Problem variables: 'database'

Clearing the workspace and re-connecting to the `Spark` cluster does not fix the issue (technically this is a a re-used connection, not a fresh connection):

``` r
rm(list=ls())
gc()
```

    ##          used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells 508500 27.2     940480 50.3   698844 37.4
    ## Vcells 696905  5.4    1308461 10.0   946160  7.3

``` r
sc <- spark_connect(master = "local",
                    version = "2.1.0")
```

    ## Re-using existing Spark connection to local

``` r
DBI::dbListTables(sc)
```

    ## Error: Variables must be length 1 or 1.
    ## Problem variables: 'database'

The point is: you are going to make a mistake at least this bad when working with real data. Rehearse how to deal with this before you attempt real work.
