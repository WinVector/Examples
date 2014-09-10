package com.mzlabs.count.Minkowski;

import java.util.BitSet;
import java.util.Date;
import java.util.HashSet;
import java.util.Set;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.divideandconquer.IntMat;
import com.mzlabs.count.divideandconquer.IntMat.RowDescription;
import com.mzlabs.count.util.IntVec;
import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.colt.ColtMatrix;

/**
 * For A x = b1, A x = b2 (x>=0, A totally unimodular)
 * find conditions such that { x | A x = b1, x>=0 } + { x | A x = b2, x>=0 } (Minkowski sum) =  { x | A x = b1 + b2, x>=0 }
 * From pp. 55-57 of John Mount Ph.D. thesis
 * @author johnmount
 *
 */
public final class Cones {
	private final int[][] Ain; // original matrix
	private final RowDescription[] rowDescr; // map from Ain to full row-rank system
	private final int[][] A;  // full row-rank sub-row system
	private final IntVec[] checkRows;

	
	/**
	 * @param A totally unimodular matrix with non-zero number of rows
	 */
	public Cones(final int[][] Ain) {
		this.Ain = Ain;
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
		checkRows = rows.toArray(new IntVec[rows.size()]);
	}
	
	public BitSet rhsGroup(final int[] bIn) {
		final int[] b = IntMat.mapVector(rowDescr,bIn); // TODO: check linear relns on map
		final int ncheck = checkRows.length;
		final int m = A.length;
		final BitSet group = new BitSet(ncheck);
		for(int i=0;i<ncheck;++i) {
			final IntVec row = checkRows[i];
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

	public static void main(final String[] args) {
		// just check if building the check-rows has any value or we could just use {-1,0,1}^bdim which has at least all the rows
		// could also just look for rows that send one column of A to a vector with one 1 and the rest zeros.
		System.out.println("n" + "\t" + "bdim" + "\t" + "nCheckRows" + "\t" + "2b^dim" + "\t" + "3^bdim" + "\t" + "date");
		for(int n=1;n<=5;++n) {
			final CountingProblem prob = new ContingencyTableProblem(n,n);
			final Cones cones = new Cones(prob.A);
			final int bdim = cones.checkRows[0].dim();
			System.out.println("" + n + "\t" + bdim + "\t" + cones.checkRows.length + "\t" +
			Math.pow(2.0,bdim) + "\t"  + Math.pow(3.0,bdim) + "\t" + new Date());
		}
	}
}
