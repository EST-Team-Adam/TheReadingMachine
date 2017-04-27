kalman_filter <- function(y) {

## MEMORY PRE-ALLOCATION ##

sentiment_filtered <- list(NA,NA)

## CONSTANTS ##
dt <- ct <- matrix(0)
Zt <- Tt <- matrix(1)

a0 <- y[1] 
P0 <- matrix(100) 

## PARAMETERS ESTIMATION ##
fit.fkf <- optim(c(HHt = var(y, na.rm = TRUE) * .5,
                 GGt = var(y, na.rm = TRUE) * .5),
                 fn = function(par, ...)
                 -fkf(HHt = matrix(par[1]), 
                      GGt = matrix(par[2]), ...)$logLik,
                 yt = rbind(y), a0 = a0, P0 = P0, dt = dt, ct = ct,
                 Zt = Zt, Tt = Tt, check.input = FALSE)

## FILTER ##
fkf.obj <- fkf(a0, 
               P0, 
               dt, 
               ct, 
               Tt, 
               Zt, 
               HHt = matrix(fit.fkf$par[1]),
               GGt = matrix(fit.fkf$par[2]), yt = rbind(y))

## COMPARISONS
fit.stats <- StructTS(y, type = "level")
fit.fkf$par
fit.stats$coef

filtered_sentiment <- list(fkf.obj,y)

return(filtered_sentiment)

}
