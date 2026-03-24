// Mock data for the Solana blockchain analytics dashboard

export const mockTransactions = [
  {
    signature: "3kJ8...9xMp",
    block: "245891234",
    time: "2026-03-22 10:34:21",
    action: "Transfer",
    by: "7vK2...3mNq",
    value: "12.5",
    fee: "0.000005",
    programs: "System Program",
  },
  {
    signature: "9mP4...2qLx",
    block: "245891198",
    time: "2026-03-22 10:28:15",
    action: "Swap",
    by: "9tR5...8pWk",
    value: "45.2",
    fee: "0.00015",
    programs: "Jupiter, Token Program",
  },
  {
    signature: "7xL9...5nKp",
    block: "245891156",
    time: "2026-03-22 10:22:08",
    action: "Stake",
    by: "2wQ8...6vFm",
    value: "100.0",
    fee: "0.000005",
    programs: "Stake Program",
  },
  {
    signature: "4pN2...8yJr",
    block: "245891089",
    time: "2026-03-22 10:15:42",
    action: "Transfer",
    by: "5kM3...9tBx",
    value: "5.75",
    fee: "0.000005",
    programs: "System Program",
  },
  {
    signature: "8qW6...3hVn",
    block: "245891034",
    time: "2026-03-22 10:09:18",
    action: "NFT Mint",
    by: "6nP7...4wLm",
    value: "0.0",
    fee: "0.01",
    programs: "Metaplex, Token Program",
  },
];

export const mockTransfers = [
  {
    from: "7vK2...3mNq",
    to: "9tR5...8pWk",
    amount: "12.5",
    token: "SOL",
    action: "Send",
  },
  {
    from: "9tR5...8pWk",
    to: "2wQ8...6vFm",
    amount: "450",
    token: "USDC",
    action: "Send",
  },
  {
    from: "2wQ8...6vFm",
    to: "5kM3...9tBx",
    amount: "1,250",
    token: "BONK",
    action: "Send",
  },
  {
    from: "5kM3...9tBx",
    to: "6nP7...4wLm",
    amount: "5.75",
    token: "SOL",
    action: "Send",
  },
  {
    from: "Jupiter Program",
    to: "7vK2...3mNq",
    amount: "890",
    token: "JUP",
    action: "Receive",
  },
];

export const mockDeFiActivities = [
  {
    action: "Swap",
    platform: "Jupiter",
    source: "SOL → USDC",
    amount: "45.2 SOL",
    value: "$8,145.60",
  },
  {
    action: "Add Liquidity",
    platform: "Raydium",
    source: "SOL-USDC LP",
    amount: "100 SOL + 18,000 USDC",
    value: "$36,000.00",
  },
  {
    action: "Stake",
    platform: "Marinade Finance",
    source: "mSOL",
    amount: "100 SOL",
    value: "$18,000.00",
  },
  {
    action: "Borrow",
    platform: "Solend",
    source: "USDC",
    amount: "5,000 USDC",
    value: "$5,000.00",
  },
  {
    action: "Claim Rewards",
    platform: "Orca",
    source: "ORCA Rewards",
    amount: "125 ORCA",
    value: "$287.50",
  },
];

export const mockNFTActivities = [
  {
    nftName: "Okay Bear #4512",
    price: "65.5 SOL",
    collection: "Okay Bears",
    marketplace: "Magic Eden",
    fromTo: "5kM3...9tBx → You",
  },
  {
    nftName: "DeGod #8234",
    price: "120.0 SOL",
    collection: "DeGods",
    marketplace: "Tensor",
    fromTo: "You → 9tR5...8pWk",
  },
  {
    nftName: "SMB #2891",
    price: "32.8 SOL",
    collection: "Solana Monkey Business",
    marketplace: "Magic Eden",
    fromTo: "2wQ8...6vFm → You",
  },
  {
    nftName: "Mad Lads #6745",
    price: "95.2 SOL",
    collection: "Mad Lads",
    marketplace: "Tensor",
    fromTo: "You → 6nP7...4wLm",
  },
  {
    nftName: "Claynosaurz #3456",
    price: "48.5 SOL",
    collection: "Claynosaurz",
    marketplace: "Magic Eden",
    fromTo: "7vK2...3mNq → You",
  },
];
