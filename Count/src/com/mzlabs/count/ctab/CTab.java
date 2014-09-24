package com.mzlabs.count.ctab;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Date;
import java.util.Set;
import java.util.TreeSet;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.divideandconquer.DivideAndConquerCounter;
import com.mzlabs.count.op.IntFunc;
import com.mzlabs.count.op.Reducer;
import com.mzlabs.count.op.impl.SimpleSum;
import com.mzlabs.count.op.impl.ThreadedSum;
import com.mzlabs.count.op.iter.OrderStepperTot;
import com.mzlabs.count.util.Fitter;
import com.mzlabs.count.util.LogLinearFitter;
import com.mzlabs.count.zeroone.ZeroOneCounter;


public final class CTab {
	
	private static final class CPair {
		public final ContingencyTableProblem prob;
		public final NonNegativeIntegralCounter counter;
		
		public CPair(final ContingencyTableProblem prob, final NonNegativeIntegralCounter counter) {
			this.prob = prob;
			this.counter = counter;
		}
	}
	
	private final boolean runParallel;
	private final CPair[][] subCounters;
	
	public CTab(final int maxRowColSize, final boolean runParallel) {
		this.runParallel = runParallel;
		subCounters = new CPair[maxRowColSize+1][maxRowColSize+1];
	}
	
	
	/**
	 * count number of rowsCols by rowsCols contingency table fill-ins with all rows/columns summing to total
	 * @param rowsCols >0
	 * @param total
	 * @return
	 */
	public BigInteger countSqTables(final int rowsCols, final int total) {
		if(rowsCols<=0) {
			throw new IllegalArgumentException();
		}
		if(rowsCols>=subCounters.length) {
			throw new IllegalArgumentException();
		}
		if(total<0) {
			return BigInteger.ZERO;
		}
		if((total==0)||(rowsCols==1)) {
			return BigInteger.ONE;
		}
		// now know rowsCols>1 and total>0, split into semi-regular tables
		final int n1 = rowsCols/2;
		final int n2 = rowsCols - n1;		
		final Set<Integer> subDims = new TreeSet<Integer>();
		subDims.add(n1);
		subDims.add(n2);
		for(final int v1: subDims) {
			for(final int v2: subDims) {
				if((0<v1)&&(v1<=v2)) {
					if(null==subCounters[v1][v2]) {
						subCounters[v1][v2] = getSubCounter(v1,v2);
					}
				}
			}
		}		
		final int targetSum = n1*total;
		final OrderStepperTot stepper = new OrderStepperTot(rowsCols,total,targetSum);
		final IntFunc subF = new IntFunc() {
			@Override
			public BigInteger f(final int[] x) {
				final BigInteger xCount = countSemiTables(n1,total,x);
				if(xCount.compareTo(BigInteger.ZERO)>0) {
					final int[] y = new int[rowsCols];
					for(int i=0;i<rowsCols;++i) {
						y[i] = total - x[i];
					}
					final BigInteger yCount = countSemiTables(n2,total,y);
					if(yCount.compareTo(BigInteger.ZERO)>0) {
						final BigInteger nperm = stepper.nPerm(x);
						final BigInteger term = nperm.multiply(xCount).multiply(yCount);
						synchronized (this) {
							return term;
						}
					}
				}
				return BigInteger.ZERO;
			}
		};
		final Reducer summer = runParallel?new ThreadedSum():new SimpleSum();
		final BigInteger sum = summer.reduce(subF,stepper);
		return sum;
	}
	
	private static CPair getSubCounter(final int nRows, final int nCols) {
		final ContingencyTableProblem cp = new ContingencyTableProblem(nRows,nCols);
		final NonNegativeIntegralCounter cnt;
		if(nRows*nCols<=28) {
			cnt = new ZeroOneCounter(cp,true);
		} else {
			cnt = new DivideAndConquerCounter(cp,false,false,true);
		}
		return new CPair(cp,cnt);
	}
	
	public String cacheSizesString() {
		synchronized (subCounters) {
			final StringBuilder b = new StringBuilder();
			b.append("{");
			for(int i=0;i<subCounters.length;++i) {
				for(int j=0;j<subCounters[i].length;++j) {
					final CPair counter = subCounters[i][j];
					if(null!=counter) {
						b.append(" [" + i + "," + j + "]:" + counter.counter.cacheSize());		
					}
				}
			}
			b.append(" }");
			return b.toString();
		}
	}
	
	public void clearCaches() {
		synchronized (subCounters) { 
			for(final CPair[] row: subCounters) {
				for(final CPair cij: row) {
					if(null!=cij) {
						cij.counter.clearCache();
					}
				}
			}
		}
	}

	/**
	 * count number of contingency table fill-ins with nCols (all summing to colBound) and rows summing to rowBounds 
	 * @param nCols >0
	 * @param colTotal >0
	 * @param rowBounds
	 * @return
	 */
	private BigInteger countSemiTables(final int nCols, final int colTotal, final int[] rowTotals) {
		final int nRows = rowTotals.length;		
		final int n1 = nRows/2;
		final int n2 = nRows - n1;
		int rowSum1 = 0;
		final int[] rowTotals1 = new int[n1];
		for(int i=0;i<n1;++i) {
			rowSum1 += rowTotals[i];
			rowTotals1[i] = rowTotals[i];
		}	
		final int[] rowTotals2 = new int[n2];
		for(int i=0;i<n2;++i) {
			rowTotals2[i] = rowTotals[n1+i];
		}
		final int targetSum = rowSum1;
		final OrderStepperTot stepper =  new OrderStepperTot(nCols,colTotal,targetSum);
		final IntFunc subF = new IntFunc() {
			@Override
			public BigInteger f(final int[] x) {
				final BigInteger xCount = countTablesSub(rowTotals1,x);
				if(xCount.compareTo(BigInteger.ZERO)>0) {
					final int[] y = new int[nCols];
					for(int i=0;i<nCols;++i) {
						y[i] = colTotal - x[i];
					}
					final BigInteger yCount = countTablesSub(rowTotals2,y);
					if(yCount.compareTo(BigInteger.ZERO)>0) {
						final BigInteger nperm = stepper.nPerm(x);
						return nperm.multiply(xCount).multiply(yCount);
					}
				}
				return BigInteger.ZERO;
			}
		};
		final Reducer summer = new SimpleSum();
		final BigInteger sum = summer.reduce(subF,stepper);
		return sum;
	}
	
	private BigInteger countTablesSub(final int[] rowTotalsIn, final int[] colTotalsIn) {
		final int[] rowTotals;
		final int[] colTotals;
		if(rowTotalsIn.length>colTotalsIn.length) {
			// swap
			rowTotals = colTotalsIn;
			colTotals = rowTotalsIn;
		} else {
			rowTotals = rowTotalsIn;
			colTotals = colTotalsIn;
		}
		// delegate problem
		final CPair counter = subCounters[rowTotals.length][colTotals.length];
		final int[] b = counter.prob.encodeB(rowTotals,colTotals);
		return counter.counter.countNonNegativeSolutions(b);
	}

	public static BigInteger debugConfirmSqTables(final int rowsCols, final int total) {
		final int[] b = new int[2*rowsCols];
		Arrays.fill(b,total);
		return getSubCounter(rowsCols,rowsCols).counter.countNonNegativeSolutions(b);
	}
	
	public static void main(final String[] args) {
		System.out.println("n" + "\t" + "total" + "\t" + "target" + "\t" + "count" + "\t" + "date" + "\t" + "cacheSizes" + "\t" + "tableFinishTimeEst");
		for(int n=1;n<=9;++n) {
			final CTab ctab = new CTab(n,true);
			final Fitter lf = new LogLinearFitter();
			final int tLast = (n*n-3*n+2)/2;
			for(int total=0;total<=tLast;++total) {
				final Date startTime = new Date();
				final BigInteger count = ctab.countSqTables(n,total);
				final String cacheSizes = ctab.cacheSizesString();
				final Date curTime = new Date();
				long remainingTimeEstMS = 10000;
				if(total>2) { 
					// simplistic model: time ~ exp(a + b*size)
					final double[] x = { total };
					final double y = 10000.0+curTime.getTime() - startTime.getTime();
					lf.addObservation(x,y,1.0);
					if(total>6) {
						final double[] beta = lf.solve();
						double timeEstMS = 0.0;
						for(int j=total+1;j<=tLast;++j) {
							final double predict = lf.predict(beta,new double[] {j});
							timeEstMS += predict;
						}
						remainingTimeEstMS = (long)Math.ceil(timeEstMS);
					}
				}
				final Date finishTimeEst = new Date(curTime.getTime()+remainingTimeEstMS);
				System.out.println("" + n + "\t" + total + "\t" + tLast + "\t" + count + "\t" + curTime + "\t" + cacheSizes + "\t" + finishTimeEst);
			}
			ctab.clearCaches();
		}
	}

}
