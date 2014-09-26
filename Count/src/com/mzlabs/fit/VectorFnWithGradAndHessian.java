package com.mzlabs.fit;

import com.winvector.linalg.colt.ColtMatrix;

public interface VectorFnWithGradAndHessian {
	public double evalEst(double[] beta, double[] x);
	public double lossAndGradAndHessian(Iterable<Obs> obs, double[] beta, double[] grad, ColtMatrix hessian);
}
