#!/bin/bash

CDIR=lib

mkdir bin

CP=$CDIR/Colt-1.2.0.jar:$CDIR/jblas-1.2.3.jar:$CDIR/commons-math3-3.0.jar:$CDIR/WVLPSolver.jar
javac -cp $CP -sourcepath src -d bin `find src -name \*.java`

java -Xmx6G -cp $CP:bin com.mzlabs.count.ctab.CTab > CTabRunLog.txt 2>&1 
