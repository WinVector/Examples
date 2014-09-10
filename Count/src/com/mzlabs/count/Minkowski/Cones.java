package com.mzlabs.count.Minkowski;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.BitSet;
import java.util.Comparator;
import java.util.Date;
import java.util.HashSet;
import java.util.Set;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.divideandconquer.IntMat;
import com.mzlabs.count.divideandconquer.IntMat.RowDescription;
import com.mzlabs.count.util.IntVec;
import com.winvector.linalg.DenseVec;
import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.colt.ColtMatrix;
import com.winvector.lp.LPEQProb;
import com.winvector.lp.LPException;
import com.winvector.lp.LPException.LPMalformedException;
import com.winvector.lp.LPSoln;
import com.winvector.lp.impl.RevisedSimplexSolver;

/**
 * For A x = b1, A x = b2 (x>=0, A totally unimodular)
 * find conditions such that { x | A x = b1, x>=0 } + { x | A x = b2, x>=0 } (Minkowski sum) =  { x | A x = b1 + b2, x>=0 }
 * From pp. 55-57 of John Mount Ph.D. thesis
 * @author johnmount
 *
 */
public final class Cones {
	private final RowDescription[] rowDescr; // map from Ain to full row-rank system
	private final int[][] A;  // full row-rank sub-row system
	private final IntVec[] checkVecs;

	
	/**
	 * @param A totally unimodular matrix with non-zero number of rows
	 */
	public Cones(final int[][] Ain) {
		rowDescr = IntMat.buildMapToCannon(Ain);
		A = IntMat.rowRestrict(Ain,rowDescr);
		final LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
		final int m = A.length;
		final int n = A[0].length;
		final SetStepper setStepper = new SetStepper(m,n);
		final int[] columnSelection = setStepper.first();
		final Set<IntVec> rows = new HashSet<IntVec>();
		do {
			final ColtMatrix mat = factory.newMatrix(m,m,false);
			for(int i=0;i<m;++i) {
				for(int j=0;j<m;++j) {
					mat.set(i,j,A[i][columnSelection[j]]);
				}
			}
			try {
				final ColtMatrix inv = mat.inverse();
				for(int i=0;i<m;++i) {
					final int[] v = new int[m];
					for(int j=0;j<m;++j) {
						final double vijR = inv.get(i,j);
						final int vij = (int)Math.round(vijR);
						if(Math.abs(vij-vijR)>1.0e-5) {
							throw new IllegalArgumentException("Matrix wasn't TU");
						}
						v[j] = vij;
					}
					rows.add(new IntVec(v));
				}
			} catch (Exception ex) {
			}
		} while(setStepper.next(columnSelection));
		checkVecs = rows.toArray(new IntVec[rows.size()]);
	}
	
	private BitSet rhsGroup(final int[] b) {
		final int ncheck = checkVecs.length;
		final int m = A.length;
		final BitSet group = new BitSet(ncheck);
		for(int i=0;i<ncheck;++i) {
			final IntVec row = checkVecs[i];
			int dot = 0;
			for(int j=0;j<m;++j) {
				dot += row.get(j)*b[j];
			}
			if(dot>=0) {
				group.set(i);
			}
		}
		return group;
	}
	
	private int[] placeWedgeBase(final int b[], final BitSet group) throws LPException {
		final int ncheck = checkVecs.length;
		final int m = A.length;
		final int n = A[0].length;
		final LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
		final int totalRows = (m+1)*ncheck;
		final int probDim = m + totalRows;
		final int degree = n-m;
		final ColtMatrix mat = factory.newMatrix(totalRows,probDim,true);
		final double[] rhs = new double[totalRows];
		final double[] obj = new double[probDim];
		for(int i=0;i<m;++i) {
			obj[i] = 1.0;
		}
		int row = 0;
		int slackVar = m;
		// put in first set of conditions
		for(int i=0;i<ncheck;++i) {
			if(group.get(i)) {
				// expect checkVecs[i].x >= 0, so: checkVecs[i].x - slack = 0
				for(int j=0;j<m;++j) {
					mat.set(row,j,checkVecs[i].get(j));
				}
				mat.set(row,slackVar,-1.0);
			} else {
				// expect checkVecs[i].x <= -1 so: -checkVecs[i].x - slack = 1
				for(int j=0;j<m;++j) {
					mat.set(row,j,-checkVecs[i].get(j));
				}
				mat.set(row,slackVar,-1.0);
				rhs[row] = 1.0;
			}
			++slackVar;
			++row;
		}
		// put in additional wedge conditions
		for(int k=0;k<m;++k) {
			for(int i=0;i<ncheck;++i) {
				if(group.get(i)) {
					// expect checkVecs[i]*(x+degree*Ek) >= 0, so: checkVecs[i].x - slack = -degree*checkVecs[i][k];
					for(int j=0;j<m;++j) {
						mat.set(row,j,checkVecs[i].get(j));
					}
					mat.set(row,slackVar,-1.0);
					rhs[row] = -degree*checkVecs[i].get(k);
				} else {
					// expect checkVecs[i].(x+degree*Ek) <= -1 so: -checkVecs[i].x - slack = 1 + degree*checkVecs[i][k]
					for(int j=0;j<m;++j) {
						mat.set(row,j,-checkVecs[i].get(j));
					}
					mat.set(row,slackVar,-1.0);
					rhs[row] = 1.0 + degree*checkVecs[i].get(k);
				}
				++slackVar;
				++row;
			}
		}
		if(row!=totalRows) {
			throw new IllegalStateException("wrong number of rows in LP");
		}
		if(slackVar!=probDim) {
			throw new IllegalStateException("wrong number of variables in LP");
		}
		final LPEQProb prob = new LPEQProb(mat.columnMatrix(),rhs,new DenseVec(obj));
		final RevisedSimplexSolver solver = new RevisedSimplexSolver();
		final LPSoln soln = solver.solve(prob, null, 1.0e-5, 1000, factory);
		final int[] base = new int[m];
		for(int i=0;i<m;++i) {
			base[i] = (int)Math.round(soln.primalSolution.get(i));
		}
		return base;
	}
	
	private static final class BitComp implements Comparator<BitSet> {
		@Override
		public int compare(final BitSet a, final BitSet b) {
			final int la = a.length();
			final int lb = b.length();
			if(la!=lb) {
				if(la>=lb) {
					return 1;
				} else {
					return -1;
				}
			}
			for(int i=0;i<la;++i) {
				final boolean av = a.get(i);
				final boolean bv = b.get(i);
				if(av!=bv) {
					if(av) {
						return 1;
					} else {
						return -1;
					}
				}
			}
			return 0;
		}
	}
	public static final Comparator<BitSet> compBitSet = new BitComp();
	
	public BigInteger getCount(final int[] bIn) throws LPException {
		final int m = A.length;
		final int n = A[0].length;
		final int degree = n-m;
		final int[] b = IntMat.mapVector(rowDescr,bIn); // TODO: check linear relns on map
		final BitSet group = rhsGroup(b);   // TODO: cache on group
		final int[] wedgeBase = placeWedgeBase(b,group); 
		final BitSet baseGroup = rhsGroup(wedgeBase);
		System.out.println(compBitSet.compare(group,baseGroup));
		for(int i=0;i<m;++i) {
			final int[] wi = Arrays.copyOf(wedgeBase,wedgeBase.length);
			wi[i] = wedgeBase[i] + degree;
			final BitSet baseGroupI = rhsGroup(wi);
			System.out.println(compBitSet.compare(group,baseGroupI));
		}
		return null;
	}

	public static void main1(final String[] args) {
		// just check if building the check-rows has any value or we could just use {-1,0,1}^bdim which has at least all the rows
		// could also just look for rows that send one column of A to a vector with one 1 and the rest zeros.
		System.out.println("n" + "\t" + "bdim" + "\t" + "nCheckRows" + "\t" + "2b^dim" + "\t" + "3^bdim" + "\t" + "date");
		for(int n=1;n<=5;++n) {
			final CountingProblem prob = new ContingencyTableProblem(n,n);
			final Cones cones = new Cones(prob.A);
			final int bdim = cones.checkVecs[0].dim();
			System.out.println("" + n + "\t" + bdim + "\t" + cones.checkVecs.length + "\t" +
			Math.pow(2.0,bdim) + "\t"  + Math.pow(3.0,bdim) + "\t" + new Date());
		}
	}
	
	public static void main(final String[] args) throws LPException {
		final int n = 2;
		final CountingProblem prob = new ContingencyTableProblem(n,n);
		final Cones cones = new Cones(prob.A);
		final int b[] = new int[] { 50, 100, 90, 60};
		System.out.println(cones.getCount(b));
	}
}
