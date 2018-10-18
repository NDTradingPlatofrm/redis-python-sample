using ND.Trading.Platform.Models;
using ND.Trading.Platform.Oanda;
using ND.Trading.Utilities;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Configuration;


namespace ND.Trading.Platform.TDM
{
    //Added for TDM comments by Dinu
    public class OandaTDM : TDManager
    {
        private Dictionary<string, List<TDMData>> InstrumentList { get; set; }
        private List<OandaAccount> AccountInfoList { get; set; }
        private OandaAccountManager AccountManager { get; set; }
        private int TDMInterval { get; set; }
        private List<IndexData> PositionIndexList { get; set; } //Change to List of index

        //constructor
        public OandaTDM(ExchangeConfig config)
            : base(config)
        {
            Dictionary<string, string> headers = new Dictionary<string, string>()
            {
                { "Authorization", "Bearer "  + this.AuthVal.Token}/*,
                { "Accept-Encoding", "gzip, deflate" },*/
            };

            ApiClient = new TokenClient(this.AuthVal, headers, this.ApiDelay);
            InstrumentList = new Dictionary<string, List<TDMData>>();
            AccountManager = new OandaAccountManager();
            AccountInfoList = new List<OandaAccount>();
            TDMInterval = Convert.ToInt32(ConfigurationManager.AppSettings["TdmIntervel"].ToString()) * -1;
            PositionIndexList = new List<IndexData>();
        }
        private OandaAccount
            GetAccount(string id)
        {
            OandaAccount rtnVal = null;
            foreach (OandaAccount act in AccountInfoList)
            {
                if (act.Id == id)
                    rtnVal = act;
            }
            return rtnVal;
        }
        private string GetLastOrderId(string id)
        {
            string orderId = "0";
            IAccount acct = GetAccount(id);
            if (acct.OrderList.Count > 0)
                orderId = acct.OrderList[0].Id;
            return orderId;
        }
        private string GetLastTradeId(string id)
        {
            IAccount acct = GetAccount(id);
            return ((OandaAccount)acct).LastTransactionId;
        }
        private List<TDMData> GetInstrumentList(string symbol)
        {
            List<TDMData> rtnVal = null;
            foreach (KeyValuePair<string, List<TDMData>> insLst in InstrumentList)
            {
                if (insLst.Key == symbol)
                {
                    rtnVal = insLst.Value;
                    break;
                }
            }
            return rtnVal;
        }
        private TDMData GetInstrument(string symbol, int pos)
        {
            TDMData rtnVal = null;
            List<TDMData> TDMList = GetInstrumentList(symbol);
            //if (PositionIndex == (TDMList.Count - 1))
            //{
            //    rtnVal = TDMList[PositionIndex]; //Change to List of index
            //    //Get the next set of list from Oanda server;
            //    List<TDMData> instrList = GetSymbolPriceList(rtnVal.Symbol, rtnVal.DTValue);
            //    InstrumentList.Remove(rtnVal.Symbol);
            //    InstrumentList.Add(rtnVal.Symbol, instrList);
            //    PositionIndex = 0; //Change to List of index
            //}
            //else
            //{
            //    PositionIndex++; //Change to List of index
            //    rtnVal = TDMList[PositionIndex];
            //}
            if (pos > -1 && pos < TDMList.Count)
                rtnVal = TDMList[pos];
            return rtnVal;
        }
        public override IAccount GetAccountDetails(string accountId)
        {
            OandaAccount accountInfo = null;
            accountInfo = GetAccount(accountId);
            if (accountInfo == null)
            {
                accountInfo = AccountManager.CreateAccount(accountId, AccountConfigList.Find(x => x.Id == accountId));
                AccountInfoList.Add(accountInfo);
            }
            return accountInfo;
        }
        public override void GetAccountChanges(IAccount act)
        {
            //Nothing to do with this function if this is TDM test
            UpdatePositionIndex((OandaAccount)act);
            AccountManager.UpdateAccount((OandaAccount)act, PositionIndexList);
        }
        public void UpdatePositionIndex(OandaAccount a)
        {
            foreach (Position pos in a.PositionList)
            {
                if (a.Type == "Long")
                    PositionIndexList.Find(x => x.Symbol == pos.Symbol).LongIndex++;
                else if (a.Type == "Short")
                    PositionIndexList.Find(x => x.Symbol == pos.Symbol).ShortIndex++;
            }
        }
        public override IEnumerable<Quote> GetQuoteList(string accountId, string mode)
        {
            //This need to be changed to PRICE API
            //TODO *******************************************************


            List<TDMData> instrList = null;
            List<Quote> result = new List<Quote>();
            Quote q = null;

            string[] tickerList = this.GetTickerList();
            for (int i = 0; i < tickerList.Length; i++)
            {
                instrList = GetInstrumentList(tickerList[i]);
                if (instrList == null)
                {
                    instrList = GetSymbolPriceList(tickerList[i], (DateTime.Now.AddDays(TDMInterval)));
                    InstrumentList.Add(tickerList[i], instrList);
                }
                q = new Quote();
                q.Symbol = tickerList[i];
                if (PositionIndexList.Find(x => x.Symbol == q.Symbol) == null)
                    PositionIndexList.Add(new IndexData(q.Symbol));
                if (mode == Constants.OrderAction.BUY)
                    q.LastBuyTradePrice = GetCurrentBuyPrice(q.Symbol);
                else if (mode == Constants.OrderAction.SELL)
                    q.LastSellTradePrice = GetCurrentSellPrice(q.Symbol);

                result.Add(q);
            }
                return result;
        }
        public override bool PlaceOrder(Order order, string accountId)
        {
            bool rtnVal = false;
            OandaAccount acct = null;
            Position p;
            try
            {
                order.OrderId = (Convert.ToInt32(GetLastOrderId(accountId)) + 1).ToString();
                acct = GetAccount(accountId);
                // if (order.Side == Constants.OrderAction.BUY)
                // {
                p = acct.GetForexPosition(order.Symbol);
                if (p == null)
                    acct.PositionList.Add(new ForexPosition(order));
                else
                    p.AddMoreStocks(order);

                order.Status = "FILLED";
                order.TradeId = (Convert.ToInt32(GetLastTradeId(accountId)) + 1).ToString();
                order.DoneAt = DateTime.Now;
                rtnVal = true;
                // }
                //  else if (order.Side == Constants.OrderAction.SELL)
                // {

                // }
            }
            catch (Exception ex)
            {
                throw ex;
            }
            return rtnVal;
        }
        public override decimal GetCurrentPrice(string symbol, string mode)
        {
            decimal result = 0.0m;
            try
            {
                if (mode == Constants.OrderAction.BUY)
                    result = GetCurrentBuyPrice(symbol);
                else if (mode == Constants.OrderAction.SELL)
                    result = GetCurrentSellPrice(symbol);
            }
            catch (Exception ex)
            {
                throw;
            }
            return result;
        }
        private decimal GetCurrentBuyPrice(string symbol)
        {
            decimal result = 0.0m;
            TDMData instrData = GetInstrument(symbol, PositionIndexList.Find(x => x.Symbol == symbol).LongIndex);
            result = instrData.BuyPrice;
            return result;
        }
        private decimal GetCurrentSellPrice(string symbol)
        {
            decimal result = 0.0m;
            TDMData instrData = GetInstrument(symbol, PositionIndexList.Find(x => x.Symbol == symbol).ShortIndex);
            result = instrData.SellPrice;
            return result;
        }

        public override Quote GetQuote(string symbol)
        {
            throw new NotImplementedException();
        }
        public override Order GetOrderInfo(string orderId)
        {
            throw new NotImplementedException();
        }
        public override decimal GetAvailablePrinciple(string currency)
        {
            throw new NotImplementedException();
        }
        public override IEnumerable<Position> GetOpenPositions(string accountId)
        {
            throw new NotImplementedException();
        }
        public override Position GetOpenPosition(string symbol, string accountId)
        {
            throw new NotImplementedException();
        }
        public override IEnumerable<TradeData> GetOpenTrades(string symbol, string accountId)
        {
            throw new NotImplementedException();
        }
        public override decimal GetLastTradePrice(string tradeId, string accountId)
        {
            throw new NotImplementedException();
        }
        //public override Transaction GetTransactionInfo(string transId, string accountId)
        //{
        //    throw new NotImplementedException();
        //}
        public override bool CloseTrade(TradeData fxS, string accountId)
        {
            throw new NotImplementedException();
        }
        public override List<TDMData> GetSymbolPriceList(string symbol, DateTime startDate)
        {
            List<TDMData> instrList = null;
            TDMData instr = null;
            string method = @"/v3/instruments/{instrument}/candles";
            method = method.Replace("{instrument}", symbol);
            string dtval = startDate.ToUniversalTime().ToString("yyyy'-'MM'-'dd'T'HH':'mm':'ss'.'ffff'Z'");
            var argsParam = "count=5000&price=BA&granularity=M1&from=" + dtval;
            string jsonResult = ApiClient.CallAsync(this.GetExchangeName(), Methods.GET, method,
                false, argsParam).Result;
            if (jsonResult != string.Empty)
            {
                instrList = new List<TDMData>();
                JToken data = JObject.Parse(jsonResult);
                JArray actArray = data["candles"].Value<JArray>();
                foreach (JObject item in actArray)
                {
                    instr = new TDMData();
                    instr.Symbol = symbol;
                    instr.DTValue = item["time"].Value<DateTime>();
                    var cnd = item["ask"].Value<JObject>();
                    instr.BuyPrice = cnd["c"].Value<decimal>();
                    cnd = item["bid"].Value<JObject>();
                    instr.SellPrice = cnd["c"].Value<decimal>();
                    instrList.Add(instr);
                }
            }
            return instrList;
        }
    }

    public class IndexData
    {
        public string Symbol { get; set; }
        public int LongIndex { get; set; }
        public int ShortIndex { get; set; }

        public IndexData(string symb)
        {
            Symbol = symb;
            LongIndex = 0;
            ShortIndex = 0;
        }
    }
}

