export const balanceReducer = (balance: any, coin: { asset: string; balance: string; withdrawAvailable: string; }) => {
  return {
    ...balance,
    [coin.asset]: {
      totalBalance: Number(coin.balance),
      availableBalance: Number(coin.withdrawAvailable)
    }
  }
}