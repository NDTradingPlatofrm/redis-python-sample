private void SetBalanceTrade()
        {
            DataAnalyzer dt = null;
            bool saveFlag = false;

            decimal shortCount = 0.0m;
            decimal longCount = 0.0m;
            if (this.CurrentAccount.Type == "Long")
            {
                shortCount = Math.Abs(ShortAccountInfo.PositionList.Find(x => x.Symbol == this.StockObject.Symbol).TotalCount);
                longCount = Math.Abs(this.StockObject.TotalCount);
            }
            else
            {
                longCount = Math.Abs(LongAccountInfo.PositionList.Find(x => x.Symbol == this.StockObject.Symbol).TotalCount);
                shortCount = Math.Abs(this.StockObject.TotalCount);
            }

            WeighBalanceData wData = new WeighBalanceData(this.StockObject.Symbol, LongAccountInfo.Id, ShortAccountInfo.Id, posConfig.LongTradeFlag, posConfig.ShortTradeFlag);

            decimal diffCount = longCount - shortCount;
            if (Math.Abs(diffCount) > 2000)
            {
                if (diffCount > 0)
                {
                    posConfig.LongTradeFlag = false;
                    saveFlag = true;
                }
                else if (diffCount < 0)
                {
                    posConfig.ShortTradeFlag = false;
                    saveFlag = true;
                }
            }
            else if (Math.Abs(diffCount) < 2000)
            {
                if (!posConfig.ShortTradeFlag)
                {
                    posConfig.ShortTradeFlag = true;
                    saveFlag = true;
                }
                if (!posConfig.LongTradeFlag)
                {
                    posConfig.LongTradeFlag = true;
                    saveFlag = true;
                }
            }



            if (saveFlag)
            {
                wData.ShortCount = shortCount;
                wData.LongCount = longCount;
                wData.ShortUProfit = ShortAccountInfo.PositionList.Find(x => x.Symbol == this.StockObject.Symbol).ProfitnLoss;
                wData.LongUProfit = LongAccountInfo.PositionList.Find(x => x.Symbol == this.StockObject.Symbol).ProfitnLoss;
                wData.ShortFlagCur = posConfig.ShortTradeFlag;
                wData.LongFlagCur = posConfig.LongTradeFlag;

                dt = new DataAnalyzer(wData);
                Thread newThread = new Thread(dt.SaveWeighBalanceData);
                newThread.Name = "AnalyzerExpSave";
                newThread.Start();
            }


            /*      Position pos = GetOtherSideSymbolCount(this.CurrentAccount.Type, this.StockObject.Symbol);
                  if (pos != null)
                  {
                      decimal otherSideSymbolCount = Math.Abs(pos.TotalCount);
                      decimal currentSymbolCount = Math.Abs(this.StockObject.TotalCount);
                      WeighBalanceData wData = new WeighBalanceData(this.StockObject.Symbol, LongAccountInfo.Id, ShortAccountInfo.Id, posConfig.LongTradeFlag, posConfig.ShortTradeFlag);
                      decimal diff = Math.Abs(currentSymbolCount - otherSideSymbolCount);
                      if (diff > 2000)
                      {
                          if (otherSideSymbolCount > currentSymbolCount) //check logic here.....
                          {
                              if (this.CurrentAccount.Type == "Short")
                                  posConfig.LongTradeFlag = false;
                              else
                                  posConfig.ShortTradeFlag = false;

                              wData.ShortCount = this.StockObject.TotalCount;
                              wData.LongCount = otherSideSymbolCount;
                              wData.ShortUProfit = this.StockObject.ProfitnLoss;
                              wData.LongUProgit = pos.ProfitnLoss;
                              wData.ShortFlagCur = posConfig.ShortTradeFlag;
                              wData.LongFlagCur = posConfig.LongTradeFlag;

                          }
                          else
                          {
                              if (this.CurrentAccount.Type == "Long")
                                  posConfig.LongTradeFlag = false;
                              else
                                  posConfig.ShortTradeFlag = false;

                              wData.LongCount = this.StockObject.TotalCount;
                              wData.ShortCount = otherSideSymbolCount;
                              wData.LongUProgit = this.StockObject.ProfitnLoss;
                              wData.ShortUProfit = pos.ProfitnLoss;
                              wData.ShortFlagCur = posConfig.ShortTradeFlag;
                              wData.LongFlagCur = posConfig.LongTradeFlag;

                          }

                          saveFlag = true;
                      }
                      if (diff < 2000)
                      {
                          posConfig.ShortTradeFlag = false ? true : true;
                          posConfig.LongTradeFlag = false ? true : true;

                          if (this.CurrentAccount.Type == "Long")
                          {
                              wData.LongCount = this.StockObject.TotalCount;
                              wData.ShortCount = otherSideSymbolCount;
                              wData.LongUProgit = this.StockObject.ProfitnLoss;
                              wData.ShortUProfit = pos.ProfitnLoss;
                              wData.ShortFlagCur = posConfig.ShortTradeFlag;
                              wData.LongFlagCur = posConfig.LongTradeFlag;
                          }
                          else if (this.CurrentAccount.Type == "Short")
                          {
                              wData.ShortCount = this.StockObject.TotalCount;
                              wData.LongCount = otherSideSymbolCount;
                              wData.ShortUProfit = this.StockObject.ProfitnLoss;
                              wData.LongUProgit = pos.ProfitnLoss;
                              wData.ShortFlagCur = posConfig.ShortTradeFlag;
                              wData.LongFlagCur = posConfig.LongTradeFlag;
                          }

                          saveFlag = true;
                      }
            
                  }*/
        }
