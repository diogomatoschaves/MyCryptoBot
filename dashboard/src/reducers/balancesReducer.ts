export const balanceReducer = (balance: any, coin: { asset: string; balance: string; availableBalance: string; }) => {
  return {
    ...balance,
    [coin.asset]: {
      totalBalance: Number(coin.balance),
      availableBalance: Number(coin.availableBalance)
    }
  }
}