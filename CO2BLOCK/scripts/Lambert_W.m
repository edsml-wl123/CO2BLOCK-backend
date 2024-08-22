function w = Lambert_W(x, branch)
    % Effective starting guess
    if nargin < 2 || branch ~= -1
        w = log(x + eps) - log(log(x + eps) + eps);  % Improved guess for primary branch
    else  
        w = log(-x + eps) - log(-log(-x + eps) + eps);  % Improved guess for lower branch
    end
    v = inf * w;  % Initialize previous value for comparison

    % Haley's method with enhanced stopping criterion
    max_iterations = 1000;  % Limit the number of iterations
    tol = 1.e-10;  % Tighter tolerance for convergence
    iter = 0;

    % Adjust loop to check if any element in the array has not converged
    while iter < max_iterations && any(abs(w(:) - v(:)) ./ abs(w(:)) > tol)
        v = w;
        e = exp(w);
        f = w .* e - x;  % Iterate to make this quantity zero
        w = w - f ./ ((e .* (w + 1) - (w + 2) .* f ./ (2 * w + 2)));
        iter = iter + 1;
    end

    % If iter == max_iterations, it might not have converged
    if iter == max_iterations
        warning('Lambert_W did not converge within the maximum number of iterations.');
    end
end
