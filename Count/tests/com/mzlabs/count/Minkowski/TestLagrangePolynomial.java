package com.mzlabs.count.Minkowski;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

import java.math.BigInteger;
import java.util.Arrays;

import org.junit.Test;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.divideandconquer.DivideAndConquerCounter;
import com.mzlabs.count.op.iter.SumStepper;
import com.mzlabs.count.util.BigRat;
import com.mzlabs.count.util.IntMat;
import com.winvector.lp.LPException;

public class TestLagrangePolynomial {
	@Test
	public void testZeroOne() {
		// Note: only testing 0/1 property, not degree of polynomial
		final int[] base = { 20, 20, 8, 12, 12 };
		final int dim = base.length;
		final int degree = 4;
		final int[] b2 = new int[dim];
		Arrays.fill(b2,100);
		final SumStepper stepper = new SumStepper(base.length,degree);
		final int[] d = stepper.first();
		final int[] z = new int[base.length];
		do {
			for(int i=0;i<z.length;++i) {
				z[i] = base[i] + d[i];
			}
			final BigRat confirmOne = LagrangePolynomial.eval(base,z,degree,z);
			assertEquals(0,BigRat.ONE.compareTo(confirmOne));
			final int[] d2 = stepper.first();
			final int[] z2 = new int[base.length];
			do {
				boolean equalsz = true;
				for(int i=0;i<z2.length;++i) {
					z2[i] = base[i] + d2[i];
					if(z2[i]!=z[i]) {
						equalsz = false;
					}
				}
				if(!equalsz) {
					final BigRat confirmZero = LagrangePolynomial.eval(base,z,degree,z2);
					assertEquals(0,BigRat.ZERO.compareTo(confirmZero));
				}
			} while(stepper.advance(d2));
		} while(stepper.advance(d));
	}
	
	@Test
	public void testConeFit() throws LPException {
		for(int n=1;n<=3;++n) {
			//System.out.println("n:" + n + "\t" + new Date());
			final CountingProblem prob = new ContingencyTableProblem(n,n);
			final NonNegativeIntegralCounter counter = new DivideAndConquerCounter(prob,true,false,true);
			final Cones cones = new Cones(prob.A);
			//System.out.println("\tcheck conditions: " + cones.checkVecs.length);
			final int b[] = new int[2*n];
			Arrays.fill(b,100);
			final int[] b2 = IntMat.mapVector(cones.rowDescr,b);
			final int[] base = cones.buildConeWedge(b);
			//System.out.println("\tinterpolation base: " + IntVec.toString(base));
			final SumStepper stepper = new SumStepper(base.length,cones.degree);
			final int[] d = stepper.first();
			final int[] z = new int[base.length];
			BigRat lagrangeEval = BigRat.ZERO;
			do {
				for(int i=0;i<z.length;++i) {
					z[i] = base[i] + d[i];
				}
				final int[] x = IntMat.pullBackVector(cones.rowDescr,z);
				final BigInteger fx = counter.countNonNegativeSolutions(x);
				final BigRat px = LagrangePolynomial.eval(base,z,cones.degree,b2);
				lagrangeEval = lagrangeEval.add(px.multiply(BigRat.valueOf(fx)));
				//System.out.println(IntVec.toString(x) + "\t" + fx + "\t" + px);
			} while(stepper.advance(d));
			//System.out.println("LagrangePolynomial\t" + lagrangeEval);
			final BigInteger lcount = lagrangeEval.intValue();
			assertNotNull(lcount);
			final BigInteger count = counter.countNonNegativeSolutions(b);
			assertEquals(0,count.compareTo(lcount));
			//System.out.println("Direct count\t" + count);
		}
	}
}
