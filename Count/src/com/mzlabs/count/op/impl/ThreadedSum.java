package com.mzlabs.count.op.impl;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

import com.mzlabs.count.op.IntFunc;
import com.mzlabs.count.op.Reducer;
import com.mzlabs.count.op.Sequencer;

public final class ThreadedSum implements Reducer {
	public int nThreads = 8;
		
	private static final class StepOrg {
		public final IntFunc f;
		public BigInteger sum = BigInteger.ZERO; // synchronize access to this on StepOrg
		
		public StepOrg(final IntFunc f) {
			this.f = f;
		}
				
		public void runStep(final int[] x) {
			final BigInteger term = f.f(x);
			if(term.compareTo(BigInteger.ZERO)!=0) {
				synchronized (this) {
					sum = sum.add(term);
				}
			}
		}
		
		public final class StepJob implements Runnable {
			private final int[] x;

			private StepJob(final int[] x) {
				this.x = Arrays.copyOf(x,x.length);
			}

			@Override
			public final void run() {
				runStep(x);
			}
		}
		
		public StepJob stepJob(final int[] x) {
			return new StepJob(x);
		}
	}

	@Override
	public BigInteger reduce(final IntFunc f, final Sequencer s) {
		final int[] x = s.first();
		if(null!=x) {
			final StepOrg stepOrg = new StepOrg(f);		
			final ArrayBlockingQueue<Runnable> workQueue = new ArrayBlockingQueue<Runnable>(20*nThreads);
			final ThreadPoolExecutor ex = new ThreadPoolExecutor(nThreads,nThreads,1000,TimeUnit.SECONDS,workQueue);
			do {
				if(workQueue.size()<=4*nThreads) {
					ex.execute(stepOrg.stepJob(x));
				} else {
					stepOrg.runStep(x);
				}
			} while(s.advance(x));
			ex.shutdown();
			while(!ex.isTerminated()) {
				try {
					ex.awaitTermination(1000, TimeUnit.SECONDS);
				} catch (InterruptedException e) {
				}
			}
			return stepOrg.sum;
		}
		return BigInteger.ZERO;
	}
}
