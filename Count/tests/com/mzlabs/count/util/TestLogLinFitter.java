package com.mzlabs.count.util;

import static org.junit.Assert.assertTrue;

import java.util.ArrayList;
import java.util.Random;

import org.junit.Test;

import com.mzlabs.fit.BalanceBasedJacobian;
import com.mzlabs.fit.BalanceJacobianCoef;
import com.mzlabs.fit.DirectPoissonJacobian;
import com.mzlabs.fit.LinearFitter;
import com.mzlabs.fit.LinkBasedGradHess;
import com.mzlabs.fit.NewtonFitter;
import com.mzlabs.fit.Obs;
import com.mzlabs.fit.SquareLossOfExp;

public class TestLogLinFitter {
	@Test
	public void testLFit() {
		final LinearFitter lf = new LinearFitter(1);
		final NewtonFitter llf = new NewtonFitter(new SquareLossOfExp());
		final Random rand = new Random(343406L);
		final ArrayList<Obs> obs = new ArrayList<Obs>();
		for(int i=1;i<7;++i) {
			final double y = Math.exp(2.0*i);
			for(int j=0;j<10;++j) {
				final double[] x = new double[] {i};
				final double yObserved = y*(1+0.3*rand.nextGaussian());
				llf.addObservation(x,yObserved,1.0);
				lf.addObservation(x,Math.log(Math.max(1.0,yObserved)),1.0);
				obs.add(new Obs(x,yObserved,1.0));
			}
		}
		final double[] lsoln = lf.solve();
		final double[] llsoln = llf.solve();
		//System.out.println("" + "y" + "\t" + "fit" + "\t" + "llfit");
		double sqLError = 0.0;
		double sqLLError = 0.0;
		for(final Obs obsi: obs) {
			final double y = obsi.y;
			final double[] x = obsi.x;
			final double lfit = Math.exp(lf.predict(lsoln, x));
			final double llfit = llf.link.evalEst(llsoln,x);
			//System.out.println("" + y + "\t" + lfit + "\t" + llfit );
			sqLError += obsi.wt*Math.pow(lfit-y,2);
			sqLLError += obsi.wt*Math.pow(llfit-y,2);
		}
		//System.out.println("errors\t" + sqLError + "\t" + sqLLError);
		assertTrue(sqLLError<sqLError);
	}
	

	@Test
	public void testPLinks() {
		final double y = 1.55528;
		final double[] x = { 5.0 };
		final Obs obs = new Obs(x,y,1.0);
		final double[] beta = { 0.2 , -0.1};
		final BalanceJacobianCoef lpgh = LinkBasedGradHess.poissonGradHess.calc(obs, beta);
		final BalanceJacobianCoef dpgh = DirectPoissonJacobian.poissonGradHess.calc(obs, beta);
		final BalanceJacobianCoef bpgh = BalanceBasedJacobian.poissonJacobian.calc(obs, beta);
		assertTrue(lpgh.absDiff(dpgh)<1.0e-8);
		assertTrue(lpgh.absDiff(bpgh)<1.0e-8);
	}
	
	@Test
	public void testPFit() {
		final NewtonFitter llf = new NewtonFitter(DirectPoissonJacobian.poissonLink);
		final ArrayList<Obs> obs = new ArrayList<Obs>();
		final Random rand = new Random(343406L);
		for(int i=1;i<=5;++i) {
			final double y = Math.exp(0.4*i) + rand.nextGaussian();
			final double[] x = new double[] {i};
			llf.addObservation(x,y,1.0);
			obs.add(new Obs(x,y,1.0));
		}
		final double[] llsoln = llf.solve();
		//System.out.println("" + "y" + "\t" + "fit" + "\t" + "llfit");
		final int dim = 2;		
		double[] sums = new double[dim];
//		double[] balance = new double[dim];
//		final LinalgFactory<ColtMatrix> factory = ColtMatrix.factory;
//		final ColtMatrix jacobian = factory.newMatrix(dim, dim, false);
//		llf.link.balanceAndJacobian(obs, llsoln, balance, jacobian);
		for(final Obs obsi: obs) {
			final double y = obsi.y;
			final double[] x = obsi.x;
			final double llfit = llf.link.evalEst(llsoln,x);
			for(int i=0;i<dim;++i) {
				final double xi = i<dim-1?obsi.x[i]:1.0;
				sums[i] += obsi.wt*xi*(y-llfit);
			}
		}
		for(final double si: sums) {
			assertTrue(Math.abs(si)<1.0e-5);
		}
	}
}
