package com.mzlabs.count.util;

import static org.junit.Assert.*;

import java.util.ArrayList;
import java.util.Random;

import org.junit.Test;

import com.mzlabs.count.util.LogLinearFitter.Obs;

public class TestLogLinFitter {
	@Test
	public void testLFit() {
		final Fitter lf = new LinearFitter(2);
		final LogLinearFitter llf = new LogLinearFitter();
		final Random rand = new Random(343406L);
		final ArrayList<Obs> obs = new ArrayList<Obs>();
		for(int i=1;i<7;++i) {
			final double y = Math.exp(2.0*i + 3.0*i*i);
			for(int j=0;j<10;++j) {
				final double[] x = new double[] {i,i*i};
				final double yObserved = y*(1+0.3*rand.nextGaussian());
				llf.addObservation(x,yObserved,1.0);
				lf.addObservation(x,Math.log(Math.max(1.0,yObserved)),1.0);
				obs.add(new Obs(x,y,1.0));
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
			final double llfit = llf.predict(llsoln, x);
			//System.out.println("" + y + "\t" + lfit + "\t" + llfit );
			sqLError += Math.pow(lfit-y,2);
			sqLLError += Math.pow(llfit-y,2);
		}
		//System.out.println("errors\t" + sqLError + "\t" + sqLLError);
		assertTrue(sqLLError<sqLError);
	}
}
