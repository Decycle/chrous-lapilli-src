import agent1Raw from './model/agent1.json'
import agent2Raw from './model/agent2.json'

const isWinning = (player, board) => {
  const checkList = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
  ]

  return checkList.some((line) =>
    line.every((index) => board[index] === player)
  )
}

const isAdjacent = (index1, index2) => {
  const x1 = index1 % 3
  const y1 = Math.floor(index1 / 3)
  const x2 = index2 % 3
  const y2 = Math.floor(index2 / 3)

  return Math.abs(x1 - x2) <= 1 && Math.abs(y1 - y2) <= 1
}

const possibleMoves = (board, currentPlayer) => {
  if (
    board.filter((cell) => cell === currentPlayer).length <
    3
  ) {
    return board
      .map((cell, index) => (cell === '' ? index : null))
      .filter((index) => index !== null)
  }

  const moves = []

  for (let i = 0; i < 9; i++) {
    if (board[i] !== currentPlayer) continue

    for (let j = 0; j < 9; j++) {
      if (board[j] !== '' || !isAdjacent(i, j)) continue
      moves.push([i, j])
    }
  }

  if (board[4] === currentPlayer) {
    return moves.filter((move) => {
      if (move[0] === 4) return true

      const newBoard = [...board]
      newBoard[move[1]] = newBoard[move[0]]
      newBoard[move[0]] = ''

      return isWinning(currentPlayer, newBoard)
    })
  }

  return moves
}

//board is a 9 element array of strings
const move = (board, currentPlayer) => {
  const boardHash = (board) =>
    board
      .map((cell) =>
        cell === '' ? 0 : cell === 'x' ? 1 : 2
      )
      .join('')

  const agent =
    currentPlayer === 'x' ? agent1Raw : agent2Raw

  const moves = possibleMoves(board, currentPlayer)

  let bestValue = -100
  let bestMove = null
  let bestBoard = null

  for (const move of moves) {
    const newBoard = [...board]

    if (!Array.isArray(move)) {
      newBoard[move] = currentPlayer
    } else {
      newBoard[move[1]] = newBoard[move[0]]
      newBoard[move[0]] = ''
    }

    const value = agent[boardHash(newBoard)] ?? 0

    if (value > bestValue) {
      bestValue = value
      bestMove = move
      bestBoard = newBoard
    }
  }

  return {
    move: bestMove,
    board: bestBoard,
  }
}

export default move
