package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.util.IntVec;
import com.mzlabs.count.zeroone.ZeroOneCounter;

final class SplitNode implements NonNegativeIntegralCounter {
	private final NonNegativeIntegralCounter leftSubSystem;
	private final NonNegativeIntegralCounter rightSubSystem;
	private final int[][] A;
	private final int m;
	private final int n;
	private final int nEntangled;
	private final boolean[][] usesRow;
	private final int[] entangledRows;
	private final boolean runParallel;
	private final boolean zeroOne;
	private final int cacheSize = 200000000;
	private final Map<IntVec,BigInteger> cache = new LinkedHashMap<IntVec,BigInteger>(1000) { // synchronize access
		private static final long serialVersionUID = 1L;

		@Override 
		 protected boolean removeEldestEntry (Map.Entry<IntVec,BigInteger> eldest) {
	         return size()>cacheSize;
	     }
	};
	
	public SplitNode(final int[][] A, final boolean[][] usesRow, final boolean runParallel,
			final NonNegativeIntegralCounter leftSubSystem,
			final NonNegativeIntegralCounter rightSubSystem,
			final boolean zeroOne) {
		this.A = A;
		this.usesRow = usesRow;
		this.runParallel = runParallel;
		this.leftSubSystem = leftSubSystem;
		this.rightSubSystem = rightSubSystem;
		this.zeroOne = zeroOne;
		m = A.length;
		n = A[0].length;
		int nE = 0;
		for(int i=0;i<m;++i) {
			if(usesRow[0][i]&&usesRow[1][i]) {
				++nE;
			}
		}
		nEntangled = nE;
		//System.out.println("split node m:" + m + ", n: " + A[0].length + ", nEntangled:" + nEntangled +
		//		", rank:" + IntMat.rowBasis(A).length);
		entangledRows = new int[nEntangled];
		nE = 0;
		for(int i=0;i<m;++i) {
			if(usesRow[0][i]&&usesRow[1][i]) {
				entangledRows[nE] = i;
				++nE;
			}
		}
	}
	
	@Override
	public boolean obviouslyEmpty(final int[] bIn) {
		return false;
	}
	
	private final class StepOrg {
		public final int[] b;
		public final IntVec bdE;
		public BigInteger accumulator = BigInteger.ZERO; // use b to sync access to accumulator
		
		public StepOrg(final int[] b, final IntVec bdE) {
			this.b = b;
			this.bdE = bdE;
		}
		
		public void runStep(final int lastVal) {
			final int[] b1 = new int[m];
			final int[] b2 = new int[m];
			for(int i=0;i<m;++i) {
				if(usesRow[0][i]) {
					b1[i] = b[i];
				}
				if(usesRow[1][i]) {
					b2[i] = b[i];
				}
			}
			final int[] counter = new int[nEntangled];
			counter[nEntangled-1] = lastVal;
			do {
				for(int ii=0;ii<nEntangled;++ii) {
					final int i = entangledRows[ii];
					b1[i] = counter[ii];
					b2[i] = b[i] - counter[ii];
				}
				// b1 + b2 == b
				// add sub1*sub2 terms, but try to avoid calculating sub(i) if sub(1-i) is obviously zero
				if((!leftSubSystem.obviouslyEmpty(b1))&&(!rightSubSystem.obviouslyEmpty(b2))) {
					final BigInteger sub1 = leftSubSystem.countNonNegativeSolutions(b1);
					if(sub1.compareTo(BigInteger.ZERO)>0) {
						final BigInteger sub2 = rightSubSystem.countNonNegativeSolutions(b2);
						if(sub2.compareTo(BigInteger.ZERO)>0) {
							final BigInteger term = sub1.multiply(sub2);
							synchronized(b) {
								accumulator = accumulator.add(term);
							}
						}
					}
				}
			} while(bdE.advanceLE(counter,nEntangled-1));
		}
		
		public final class StepJob implements Runnable {
			private final int lastVal;

			private StepJob(final int lastVal) {
				this.lastVal = lastVal;
			}

			@Override
			public final void run() {
				runStep(lastVal);
			}

		}
		
		public StepJob stepJob(final int lastVal) {
			return new StepJob(lastVal);
		}
	}
	
	@Override
	public BigInteger countNonNegativeSolutions(final int[] b) {
		final IntVec key = new IntVec(b);
		synchronized(cache) {
			final BigInteger count = cache.get(key);
			if(null!=count) {
				return count;
			}
		}
		final int[] bound = new int[nEntangled];
		for(int ii=0;ii<nEntangled;++ii) {
			final int i = entangledRows[ii];
			bound[ii] = b[i];
			if(zeroOne) {
				int rowSum = 0;
				for(int j=0;j<n;++j) {
					rowSum += A[i][j];
				}
				bound[ii] = Math.min(bound[ii],rowSum);
			}
		}
		final IntVec bdE = new IntVec(bound);
		final StepOrg stepOrg = new StepOrg(b,bdE);
		if(runParallel) {
			final ArrayBlockingQueue<Runnable> workQueue = new ArrayBlockingQueue<Runnable>(bdE.get(nEntangled-1)+2);
			final ThreadPoolExecutor ex = new ThreadPoolExecutor(4,4,1000,TimeUnit.SECONDS,workQueue);
			for(int i=0;i<bdE.get(nEntangled-1);++i) {
				final StepOrg.StepJob job = stepOrg.stepJob(i);
				ex.execute(job);
			}
			stepOrg.runStep(bdE.get(nEntangled-1));
			ex.shutdown();
			while(!ex.isTerminated()) {
				try {
					ex.awaitTermination(1000, TimeUnit.SECONDS);
				} catch (InterruptedException e) {
				}
			}
		} else {
			for(int i=0;i<=bdE.get(nEntangled-1);++i) {
				stepOrg.runStep(i);
			}
		}
		final BigInteger count = stepOrg.accumulator;
		if(DivideAndConquerCounter.debug) {
			final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b,zeroOne);
			if(check.compareTo(count)!=0) {
				throw new IllegalStateException("got wrong answer");
			}
		}
		synchronized(cache) {
			cache.put(key,count);
		}
		return count;
	}
	
	@Override
	public String toString() {
		return "split(" + A.length + "\\" + nEntangled + "," + n  + ";" + leftSubSystem + "," + rightSubSystem + ")";
	}
}
