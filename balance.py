using ND.Trading.Platform.Models;
using ND.Trading.Platform.Oanda;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ND.Trading.Platform.TDM
{
    public class OandaAccountManager
    {

        public OandaAccount CreateAccount(string accountId, AccountConfig acConfig)
        {
            OandaAccount accountInfo = new OandaAccount();
            accountInfo.Id = accountId;
            accountInfo.Name=acConfig.Name;
            accountInfo.Type = acConfig.Type;
            return accountInfo;
        }
        public void UpdateAccount(OandaAccount act, List<IndexData> posIndexList)
        {

        }
    }
}
