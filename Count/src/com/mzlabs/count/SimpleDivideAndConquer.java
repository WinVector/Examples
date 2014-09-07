package com.mzlabs.count;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.Matrix;
import com.winvector.linalg.jblas.JBlasMatrix;

/**
 * build every possible b such that A z = b is solvable for z in zero/one or non-negative integer for zero/one matrix A with no zero columns
 * useful when there are many more columns than rows
 * 
 * Not practical- slower than the naive method of enumerating all e/one z's for contingency tables until we get to probably around 20 by 20 tables.
 * 
 * @author johnmount
 *
 */

final class SimpleDivideAndConquer implements NonNegativeIntegralCounter {
	private final LinalgFactory<JBlasMatrix> factory = JBlasMatrix.factory;
	private final CountingProblem problem;
	private final boolean zeroOne;
	private Map<IntVec,LinOpCarrier<JBlasMatrix>> inverseOp = new HashMap<IntVec,LinOpCarrier<JBlasMatrix>>();
	
	private static final class LinOpCarrier<Q extends Matrix<Q>> {
		public final Q fwd;
		public Q inv = null;
		
		public LinOpCarrier(final Q fwd) {
			this.fwd = fwd;
		}
	}
	
	private final Map<DKey,BigInteger> cache = new HashMap<DKey,BigInteger>(1000);
	
	
	public static boolean acceptableA(final int[][] A) {
		final int m = A.length;
		final int n = A[0].length;
		for(int j=0;j<n;++j) {
			boolean sawNZ = false;
			for(int i=0;i<m;++i) {
				if((A[i][j]<0)||(A[i][j]>1)) {
					return false;
				}
				if(A[i][j]>0) {
					sawNZ = true;
				}
			}
			if(!sawNZ) {
				return false;
			}
		}
		return true;
	}
	
	/**
	 * 
	 * @param A non-negative zero/one matrix with no zero columns
	 * @param zeroOne if true we only consider zero/one solutions, otherwise we consider non-negative integer solutions
	 */
	public SimpleDivideAndConquer(final CountingProblem problem, final boolean zeroOne) {
		this.problem = problem;
		this.zeroOne = zeroOne;
		if(!acceptableA(problem.A)) {
			throw new IllegalArgumentException("unaccaptable matrix");
		}
	}
	
	/**
	 * 
	 * @param key
	 * @return non-null on any base-case (which must include all cases where key.columnSet.dim()<2)
	 */
	private BigInteger baseCases(final DKey key) {
		final int m = problem.A.length;
		final int np = key.columnSet.dim();
		if(np<=0) {
			throw new IllegalArgumentException("empty column set");
		}
		// If we are full column rank then we either have one or zero solutions.
		// We eventually hit this case as we have no empty columns, so all single column systems are full column rank.
		if(np<=m) {
			final double epsilon = 1.0e-8;
			LinOpCarrier<JBlasMatrix> op = inverseOp.get(key.columnSet);
			if(null==op) {
				final JBlasMatrix amat = factory.newMatrix(m,np,false);
				final JBlasMatrix amatT = factory.newMatrix(np,m,false);
				for(int i=0;i<m;++i) {
					for(int jj=0;jj<np;++jj) {
						amat.set(i,jj,problem.A[i][key.columnSet.get(jj)]);
						amatT.set(jj,i,problem.A[i][key.columnSet.get(jj)]);
					}
				}
				op = new LinOpCarrier<JBlasMatrix>(amat);
				final JBlasMatrix aTa = amatT.multMat(amat);
				try {
					final JBlasMatrix aTaI = aTa.inverse();
					boolean goodMat = true;
					final JBlasMatrix check = aTaI.multMat(aTa);
					final int k = check.rows();
					for(int i=0;(i<k)&&(goodMat);++i) {
						for(int j=0;(j<k)&&(goodMat);++j) {
							if(i==j) {
								if(Math.abs(check.get(i,j)-1.0)>epsilon) {
									goodMat = false;
								}
							} else {
								if(Math.abs(check.get(i,j))>epsilon) {
									goodMat = false;
								}
							}
						}
					}
					if(goodMat) {
						op.inv = aTaI.multMat(amatT);
					}
				} catch (Exception ex) {
				}
				inverseOp.put(key.columnSet,op);
			}
			if(null!=op.inv) {
				final double[] soln = op.inv.mult(key.b.asDouble());
				for(final double si: soln) {
					if((si<-epsilon)||(Math.abs(si-Math.round(si))>epsilon)) {
						return BigInteger.ZERO;
					}
					if(zeroOne) {
						if(si>1+epsilon) {
							return BigInteger.ZERO;
						}
					}
				}
				final double[] recovered = op.fwd.mult(soln);
				for(int i=0;i<m;++i) {
					if(Math.abs(recovered[i]-key.b.get(i))>epsilon) {
						return BigInteger.ZERO;
					}
				}
				return BigInteger.ONE;
			}
		}
		if(np<=1) {
			throw new IllegalStateException("single column not treated as full rank");
		}
		// steal from cache if possible (consider any cheap calculation base)
		return cache.get(key);
	}

	/**
	 * assumes we have already checked for basecase solutions (so in particular key.columnSet.length>1)
	 * return number of solutions to problem.A[colset] z = b with z zero/one or integer (depending on control)
	 * @param key
	 * @return
	 */
	private BigInteger solutionCountBySplit(final DKey key) {
		BigInteger cached = cache.get(key);
		if(null==cached) {
			// know we have at least 2 columns
			cached = BigInteger.ZERO;
			final int m = problem.A.length;
			//System.out.println(key);
			final int n1 = key.columnSet.dim()/2;
			final int n2 = key.columnSet.dim() - n1;
			final IntVec c1;
			{
				final int[] cset1 = new int[n1];
				for(int j=0;j<n1;++j) {
					cset1[j] = key.columnSet.get(j);
				}
				c1 = new IntVec(cset1);
			}
			final IntVec c2;
			{
				final int[] cset2 = new int[n2];
				for(int j=0;j<n2;++j) {
					cset2[j] = key.columnSet.get(j+n1);
				}
				c2 = new IntVec(cset2);				
			}
			final IntVec bd1;
			if(zeroOne) {
				final int[] bound1 = new int[m];
				for(int i=0;i<m;++i) {
					for(int jj=0;jj<n1;++jj) {
						bound1[i] += problem.A[i][c1.get(jj)];
					}
				}
				for(int i=0;i<m;++i) {
					bound1[i] = Math.min(bound1[i],key.b.get(i));
				}
				bd1 = new IntVec(bound1);
			} else {
				bd1 = key.b;
			}
			final int[] b1 = new int[m];
			final int[] b2 = new int[m];
			do {
				// add sub1*sub2 terms, but try to avoid calculating sub(i) if sub(1-i) is obviously zero
				final DKey k1 = new DKey(c1,new IntVec(b1));
				final BigInteger base1 = baseCases(k1);
				if((null==base1)||(base1.compareTo(BigInteger.ZERO)>0)) {
					for(int i=0;i<m;++i) {
						b2[i] = key.b.get(i) - b1[i];
					}
					final DKey k2 = new DKey(c2,new IntVec(b2));
					final BigInteger base2 = baseCases(k2);
					if((null==base2)||(base2.compareTo(BigInteger.ZERO)>0)) {
						final BigInteger sub1;
						if(null!=base1) {
							sub1 = base1;
						} else {
							sub1 = solutionCountBySplit(k1);
						}
						if(sub1.compareTo(BigInteger.ZERO)>0) {
							final BigInteger sub2;
							if(null!=base2) {
								sub2 = base2;
							} else {
								sub2 = solutionCountBySplit(k2);
							}
							if(sub2.compareTo(BigInteger.ZERO)>0) {
								cached = cached.add(sub1.multiply(sub2));
							}
						}
					}
				}
			} while(bd1.advanceLE(b1));
			cache.put(key,cached);
		}
		return cached;
	}
	
	/**
	 * return number of solutions to problem.A z = b with z zero/one or non-negative integer (depending on control)
	 * @param b
	 * @return
	 */
	public BigInteger countNonNegativeSolutions(final int[] bIn) {
		final int n = problem.A[0].length;
		final IntVec bvec = problem.normalForm(new IntVec(bIn));
		final int[] colset = new int[n];
		for(int i=0;i<n;++i) {
			colset[i] = i;
		}
		final DKey key = new DKey(new IntVec(colset),bvec);
		final BigInteger baseSoln = baseCases(key);
		if(null!=baseSoln) {
			return baseSoln;
		}
		return solutionCountBySplit(key);
	}
	
	/**
	 * 
	 * @return map from every b such that problem.A z = b is solvable for z zero/one to how many such z there are
	 */
	public static Map<IntVec,BigInteger> zeroOneSolutionCounts(final CountingProblem problem) {
		final SimpleDivideAndConquer dc = new SimpleDivideAndConquer(problem,true);
		final Map<IntVec,BigInteger> solnCounts = new HashMap<IntVec,BigInteger>();
		final int m = problem.A.length;
		final int n = problem.A[0].length;
		final int[] bounds = new int[m];
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				bounds[i] += problem.A[i][j];
			}
		}
		final IntVec boundsVec = new IntVec(bounds);
		final int[] b = new int[m];
		do {
			final BigInteger nsolns = dc.countNonNegativeSolutions(b);
			if(nsolns.compareTo(BigInteger.ZERO)>0) {
				solnCounts.put(new IntVec(b),nsolns);
			}
		} while(boundsVec.advanceLE(b));
//		System.out.println("dc cache size: " + dc.cache.size());
//		System.out.println("dc result size: " + solnCounts.size());
//		BigInteger total = BigInteger.ZERO;
//		for(final BigInteger ci: solnCounts.values()) {
//			total = total.add(ci);
//		}
//		System.out.println("dc total solns: " + total);
//		System.out.println("dc m,n,2^n: " + m + " " + n + " " + Math.pow(2,n));
//		System.out.println("base cases");
//		for(final Entry<IntVec, LinOpCarrier<JBlasMatrix>> me: dc.inverseOp.entrySet()) {
//			if(me.getValue().inv!=null) {
//				System.out.println("\t" + me.getKey());
//			}
//		}
		return solnCounts;
	}
	

	
	public static void workProb(final int n) {
		final CountingProblem prob = new ContingencyTableProblem(n,n);
		final SimpleDivideAndConquer dc = new SimpleDivideAndConquer(prob,false);
		final int[] b = new int[prob.A.length];
		final BigInteger[] ys = new BigInteger[(n-1)*(n-1)+1];
		for(int i= 0;i<ys.length;++i) {
			Arrays.fill(b,i);
			ys[i] = dc.countNonNegativeSolutions(b);
		}
		for(int i= 0;i<=2*n*n;++i) {
			Arrays.fill(b,i);
			final double polyEval = CountExample.evalPoly(ys,i);
			if(i<ys.length) {
				System.out.println("divideConquer(" + n + "," + n + ";" + i +")= " + ys[i]);
			}
			System.out.println("\tpoly(" + n + "," + n + ";" + i +")= " + polyEval);
		}
	}

	public static void main(final String[] args) {
		for(int n=1;n<=3;++n) {
			workProb(n);
		}
	}
}
