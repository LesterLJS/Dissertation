# Chapter 1: Introduction
## 1.1 Research Context

Options are financial contracts that give their holders the right, but not the obligation, to buy or sell an underlying asset at a predetermined price. They are widely used to manage financial risk and to express expectations about future market movements. Consequently, understanding how options are priced is important in both financial theory and practice.

The value of an option depends on several factors, including the current price of the underlying asset, the strike price, the time to maturity, the risk-free interest rate, and the volatility of the underlying asset. Volatility is particularly important because it measures the uncertainty surrounding future price movements. All else being equal, greater volatility generally increases the value of an option because it creates a wider range of possible future outcomes.

## 1.2 Problem Statement

The Black--Scholes model provides one of the most influential frameworks for pricing European options. Given the underlying asset price, strike price, time to maturity, risk-free interest rate, and volatility, the model produces a theoretical option price. Its clear mathematical structure and interpretable parameters have made it an important foundation of option-pricing theory.

A central limitation of the standard Black--Scholes model is its assumption of constant volatility. Under this assumption, options written on the same asset with the same maturity should have the same implied volatility, regardless of their strike prices. Market observations, however, commonly show that implied volatility changes across strikes. The resulting pattern may take the form of a smile, a skew, or another nonlinear shape.

This difference between the model assumption and observed market behaviour means that a single Black--Scholes model cannot always describe the full implied volatility structure.

## 1.3 Research Motivation

Machine-learning models, particularly neural networks, provide a flexible way to learn nonlinear relationships between option characteristics and prices or implied volatilities. However, this flexibility may reduce interpretability. Although a neural network can produce an accurate prediction, it may be difficult to explain that prediction using familiar financial concepts.

This dissertation investigates whether flexibility and financial interpretability can be combined. Instead of replacing Black--Scholes pricing with a completely unrestricted neural network, the proposed model uses several Black--Scholes pricing models as experts. A gating network then determines how much each expert contributes at a particular level of log-moneyness.

## 1.4 Proposed Approach

The proposed model has the following general form:

$$
\widehat{C}(x)
=
\sum_{m=1}^{M}
w_m(x)
C_{\mathrm{BS}}(S,K,T,r,\sigma_m),
$$

where $M$ is the number of experts, $\sigma_m$ is the volatility associated with expert $m$, and $w_m(x)$ is its input-dependent weight. The weights are non-negative and sum to one.

Each expert therefore remains a complete Black--Scholes pricing model. The neural network is used only to determine how the experts should be combined. This structure aims to provide greater flexibility than a single Black--Scholes model while retaining a clearer financial interpretation than a conventional neural network.

The present study evaluates this idea as a proof of concept using a synthetic implied volatility smile with a fixed maturity. It does not attempt to establish that the model will necessarily perform equally well on real market data.

## 1.5 Research Questions

This dissertation addresses the following research questions:

1. Why are constant and linear volatility models unable to represent a nonlinear implied volatility smile accurately?
2. Can a mixture of Black--Scholes experts achieve fitting accuracy comparable to that of a conventional nonlinear neural network?
3. Can the expert weights provide an interpretable description of the model's behaviour across strike prices?
4. How does the number of experts affect predictive performance and training stability?

## 1.6 Research Hypothesis

The research hypothesis is that a single global volatility level is insufficient to represent an implied volatility smile with local variation. A collection of Black--Scholes experts combined through input-dependent weights may provide a more flexible representation.

The corresponding null hypothesis is that a single global model is sufficient and that introducing multiple experts does not produce a meaningful improvement.

## 1.7 Research Contributions

The main contributions of this dissertation are:

1. the construction of a mixture-of-experts model in which each expert is a Black--Scholes pricing model;
2. a comparison with constant-volatility, linear-volatility, and multilayer-perceptron benchmarks;
3. an evaluation using both option-price and implied-volatility errors;
4. an analysis of expert weights as a source of model interpretability; and
5. an investigation of how the number of experts affects model performance.

# Chapter 2: Background
## 2.1 Options and Option Pricing

A call option gives its holder the right to buy an underlying asset at a predetermined strike price, whereas a put option gives its holder the right to sell the asset. A European option can be exercised only at its maturity date. The amount paid to purchase the option is called the option premium.

This dissertation focuses on European call options. Their values depend on the relationship between the underlying asset price and the strike price, the remaining time to maturity, interest rates, and volatility.

## 2.2 The Black--Scholes Model

For a non-dividend-paying European call option, the Black--Scholes price is

$$
C_{\mathrm{BS}}
=
S\Phi(d_1)-Ke^{-rT}\Phi(d_2),
$$

where

$$
d_1
=
\frac{
\ln(S/K)+\left(r+\frac{1}{2}\sigma^2\right)T
}{
\sigma\sqrt{T}
},
\qquad
d_2=d_1-\sigma\sqrt{T}.
$$

The variables are defined as follows:

| Symbol | Meaning |
|---|---|
| $C_{\mathrm{BS}}$ | Black--Scholes European call price |
| $S$ | Current underlying asset price |
| $K$ | Strike price |
| $T$ | Time remaining until maturity |
| $r$ | Continuously compounded risk-free interest rate |
| $\sigma$ | Volatility of the underlying asset |
| $\Phi$ | Standard normal cumulative distribution function |

In intuitive terms, the formula converts the characteristics of an option and an assumed volatility into a theoretical price. In this dissertation, Black--Scholes is not discarded. Instead, it forms the pricing mechanism inside every expert.

## 2.3 Implied Volatility

If volatility is known, the Black--Scholes formula produces an option price. Conversely, if the market price is known, it is possible to search for the volatility that makes the theoretical price equal to the observed price. This value is called implied volatility.

Mathematically, implied volatility $\sigma_{\mathrm{IV}}$ satisfies

$$
C_{\mathrm{BS}}
(S,K,T,r,\sigma_{\mathrm{IV}})
=
C_{\mathrm{market}}.
$$

This equation generally has no closed-form solution for $\sigma_{\mathrm{IV}}$, so a numerical procedure is required. This dissertation uses a bisection method to recover implied volatility from predicted option prices.

## 2.4 The Implied Volatility Smile

If the constant-volatility assumption were consistent with market prices, options with different strike prices but the same underlying asset and maturity would produce the same implied volatility. The implied volatility curve would therefore be horizontal.

In practice, implied volatility frequently changes with the strike price. When implied volatility is lower near the at-the-money region and higher at more distant strikes, the resulting curve resembles a smile. An asymmetric pattern is often described as a volatility skew.

The existence of these patterns shows that a single constant volatility cannot represent all strike regions simultaneously. This provides the central motivation for using multiple volatility experts.

## 2.5 Multilayer Perceptrons

A multilayer perceptron is a neural network composed of interconnected layers and nonlinear activation functions. In this dissertation, the MLP receives log-moneyness $x$ and predicts an implied volatility:

$$
\widehat{\sigma}(x)=f_{\theta}(x),
$$

where $\theta$ represents the trainable network parameters. The predicted volatility is then passed through the Black--Scholes formula to obtain an option price.

The MLP can represent nonlinear volatility functions, but its hidden units do not have an immediate financial interpretation. It is therefore used as a flexible but less interpretable benchmark.

## 2.6 Mixture-of-Experts Models

A mixture-of-experts model combines the outputs of several specialised models. Its general form is

$$
\widehat{y}(x)
=
\sum_{m=1}^{M}w_m(x)h_m(x),
$$

where $h_m(x)$ is the output of expert $m$ and $w_m(x)$ is its weight. The weights satisfy

$$
w_m(x)\geq 0,
\qquad
\sum_{m=1}^{M}w_m(x)=1.
$$

A softmax function can be used to produce these weights:

$$
w_m(x)
=
\frac{\exp(z_m(x))}
{\sum_{k=1}^{M}\exp(z_k(x))}.
$$

The experts provide alternative candidate outputs, while the gating network determines which experts should receive greater importance for a particular input.

## 2.7 Black--Scholes Experts

In the proposed model, expert $m$ produces a complete Black--Scholes price using its associated volatility $\sigma_m$:

$$
h_m(x_j)
=
C_{\mathrm{BS}}(S,K_j,T,r,\sigma_m).
$$

The final predicted price is

$$
\widehat{C}_j
=
\sum_{m=1}^{M}
w_m(x_j)h_m(x_j).
$$

This formulation allows different strike regions to rely on different combinations of volatility experts. The final prediction remains a weighted combination of financially meaningful Black--Scholes prices, while the expert weights provide a way to inspect how the model behaves across strikes.
