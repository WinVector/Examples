package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

import com.mzlabs.count.IntVec;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.ZeroOneCounter;

final class SplitNode implements NonNegativeIntegralCounter {
	private final NonNegativeIntegralCounter leftSubSystem;
	private final NonNegativeIntegralCounter rightSubSystem;
	private final int[][] A;
	private final boolean[][] usesRow;
	private final int[] entangledRows;
	private final boolean runParallel;
	private final Map<IntVec,BigInteger> cache = new HashMap<IntVec,BigInteger>(1000); // synchronize access
	
	public SplitNode(final int[][] A, final boolean[][] usesRow, final boolean runParallel,
			final NonNegativeIntegralCounter leftSubSystem,
			final NonNegativeIntegralCounter rightSubSystem) {
		this.A = A;
		this.usesRow = usesRow;
		this.runParallel = runParallel;
		this.leftSubSystem = leftSubSystem;
		this.rightSubSystem = rightSubSystem;
		final int m = A.length;
		int nEntangled = 0;
		for(int i=0;i<m;++i) {
			if(usesRow[0][i]&&usesRow[1][i]) {
				++nEntangled;
			}
		}
		//System.out.println("split node m:" + m + ", n: " + A[0].length + ", nEntangled:" + nEntangled +
		//		", rank:" + IntMat.rowBasis(A).length);
		entangledRows = new int[nEntangled];
		nEntangled = 0;
		for(int i=0;i<m;++i) {
			if(usesRow[0][i]&&usesRow[1][i]) {
				entangledRows[nEntangled] = i;
				++nEntangled;
			}
		}
	}
	
	private class StepOrg {
		public final int[] b;
		public BigInteger accumulator = BigInteger.ZERO; // use b to sync access to accumulator
		final int m = A.length;
		final int nEntangled = entangledRows.length;
		
		public StepOrg(final int[] b) {
			this.b = b;
		}
		
		public void runStep(final int[] counter) {
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
			for(int ii=0;ii<nEntangled;++ii) {
				final int i = entangledRows[ii];
				b1[i] = counter[ii];
				b2[i] = b[i] - counter[ii];
			}
			// add sub1*sub2 terms, but try to avoid calculating sub(i) if sub(1-i) is obviously zero
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
		
		public class StepJob implements Runnable {
			private final int[] counter;

			private StepJob(final int[] counter) {
				this.counter = Arrays.copyOf(counter,counter.length);
			}

			@Override
			public final void run() {
				runStep(counter);
			}

		}
		
		public StepJob stepJob(final int[] counter) {
			return new StepJob(counter);
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
		final int nEntangled = entangledRows.length;
		final int[] bound = new int[nEntangled];
		for(int ii=0;ii<nEntangled;++ii) {
			bound[ii] = b[entangledRows[ii]];
		}
		final IntVec bdE = new IntVec(bound);
		final  int[] counter = new int[nEntangled];
		final StepOrg stepOrg = new StepOrg(b);
		if(runParallel) {
			final ArrayBlockingQueue<Runnable> workQueue = new ArrayBlockingQueue<Runnable>(1000);
			final ThreadPoolExecutor ex = new ThreadPoolExecutor(8,8,1000,TimeUnit.SECONDS,workQueue);
			do {
				final StepOrg.StepJob job = stepOrg.stepJob(counter);
				ex.execute(job);
			} while(bdE.advanceLE(counter));
			ex.shutdown();
			while(!ex.isTerminated()) {
				try {
					ex.awaitTermination(1000, TimeUnit.SECONDS);
				} catch (InterruptedException e) {
				}
			}
		} else {
			do {
				stepOrg.runStep(counter);
			} while(bdE.advanceLE(counter));
		}
		final BigInteger count = stepOrg.accumulator;
		if(DivideAndConquerCounter.debug) {
			final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b);
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
		return "split(" + A.length + "," + A[0].length + ";" + leftSubSystem + "," + rightSubSystem + ")";
	}
}
