package com.mzlabs.fit;

import com.winvector.linalg.colt.ColtMatrix;

public interface Link {
	public double lossAndGradAndHessian(Iterable<Obs> obs, double[] beta, double[] grad, ColtMatrix hessian);
	public double inverseLink(double y);
}
