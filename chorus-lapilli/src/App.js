import logo from './logo.svg'
import './App.css'
import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react'

import { ReactComponent as Circle } from './assets/circle.svg'
import { ReactComponent as Cross } from './assets/cross.svg'

import AIMove from './AI'

const App = () => {
  const [board, setBoard] = useState([
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
  ])
  const [currentPlayer, setCurrentPlayer] = useState('x')
  const [selected, setSelected] = useState(null)
  const [result, setResult] = useState('')

  const [enableAI, setEnableAI] = useState(true)
  const [aiFirst, setAiFirst] = useState(false)

  const otherPlayer = useCallback(
    (player) => (player === 'x' ? 'o' : 'x'),
    []
  )
  const isPlacing = (player) => {
    return (
      board.filter((cell) => cell === player).length < 3
    )
  }

  const isWinning = (player, board) => {
    const winningLines = [
      [0, 1, 2],
      [3, 4, 5],
      [6, 7, 8],
      [0, 3, 6],
      [1, 4, 7],
      [2, 5, 8],
      [0, 4, 8],
      [2, 4, 6],
    ]

    return winningLines.some((line) =>
      line.every((index) => board[index] === player)
    )
  }

  const checkGameOver = useCallback((board) => {
    if (isWinning('x', board)) {
      setResult('X wins!')
    }

    if (isWinning('o', board)) {
      setResult('O wins!')
    }
  }, [])

  useEffect(() => {
    checkGameOver(board)
  }, [board, checkGameOver])

  useEffect(() => {
    if (enableAI) {
      if (
        (aiFirst && currentPlayer === 'x') ||
        (!aiFirst && currentPlayer === 'o')
      ) {
        const aiMove = AIMove(board, currentPlayer)
        setBoard(aiMove.board)
        setCurrentPlayer(otherPlayer(currentPlayer))
      }
    }
  }, [board, currentPlayer, aiFirst, enableAI, otherPlayer])

  const placeMark = (index) => {
    if (board[index] !== '' || result) return

    setBoard([
      ...board.slice(0, index),
      currentPlayer,
      ...board.slice(index + 1, board.length),
    ])

    setCurrentPlayer(otherPlayer(currentPlayer))
  }

  const selectMark = (index) => {
    if (board[index] !== currentPlayer || result) return
    console.log('selected', index)

    setSelected(index)
  }

  const cancelSelect = () => {
    setSelected(null)
  }

  const isAdjacent = (index1, index2) => {
    const x1 = index1 % 3
    const y1 = Math.floor(index1 / 3)
    const x2 = index2 % 3
    const y2 = Math.floor(index2 / 3)

    return Math.abs(x1 - x2) <= 1 && Math.abs(y1 - y2) <= 1
  }

  const canMove = (index) => {
    const newBoard = [...board]
    newBoard[index] = currentPlayer
    newBoard[selected] = ''

    return !(
      board[4] === currentPlayer &&
      selected !== 4 &&
      !isWinning(currentPlayer, newBoard)
    )
  }

  const moveMark = (index) => {
    if (result) return
    if (
      selected !== null &&
      board[index] === currentPlayer
    ) {
      setSelected(index)
      return
    }

    if (
      selected === null ||
      board[index] !== '' ||
      !isAdjacent(selected, index) ||
      !canMove(index)
    )
      return

    const newBoard = [...board]
    newBoard[index] = newBoard[selected]
    newBoard[selected] = ''

    setBoard(newBoard)
    setSelected(null)
    setCurrentPlayer(otherPlayer(currentPlayer))
  }

  const selectedStyle = (index, type) => {
    if (selected === index) {
      const animation =
        type === 'x'
          ? 'wiggleCross 1.5s linear infinite'
          : 'wiggleCircle 1.5s linear infinite'

      return {
        animation,
      }
    }
  }

  const isStuck = (index) => {
    const x = index % 3
    const y = Math.floor(index / 3)

    const adjacentCells = [
      [x - 1, y - 1],
      [x, y - 1],
      [x + 1, y - 1],
      [x - 1, y],
      [x + 1, y],
      [x - 1, y + 1],
      [x, y + 1],
      [x + 1, y + 1],
    ]

    return adjacentCells.every(
      ([x, y]) =>
        x < 0 ||
        x > 2 ||
        y < 0 ||
        y > 2 ||
        board[y * 3 + x] !== ''
    )
  }

  const cellClass = (index) => {
    if (result) return 'cell'

    const classes = ['cell']

    if (index === 4) classes.push('cell-center')

    if (isPlacing(currentPlayer) && board[index] === '') {
      classes.push('can-place')
    } else if (
      !isPlacing(currentPlayer) &&
      selected === null &&
      board[index] === currentPlayer &&
      !isStuck(index)
    ) {
      classes.push('can-select')
    } else if (
      selected !== null &&
      board[index] === '' &&
      isAdjacent(selected, index)
    ) {
      classes.push('can-move')
    }

    return classes.join(' ')
  }

  const resetGame = () => {
    setBoard(['', '', '', '', '', '', '', '', ''])
    setCurrentPlayer('x')
    setSelected(null)
    setResult('')
  }

  const [showRuleWindow, setShowRuleWindow] =
    useState(false)

  return (
    <div className='App'>
      <h1 className='title'>Chorus Lapilli</h1>
      <div className='board'>
        {board.map((cell, index) => (
          <div
            key={index}
            className={cellClass(index)}
            onClick={() => {
              if (isPlacing(currentPlayer)) {
                placeMark(index)
              } else if (selected === null) {
                if (!isStuck(index)) selectMark(index)
              } else if (selected === index) {
                cancelSelect()
              } else {
                moveMark(index)
              }
            }}>
            {cell === 'o' ? (
              <Circle
                className='cell-content'
                style={selectedStyle(index, 'o')}
              />
            ) : cell === 'x' ? (
              <Cross
                className='cell-content'
                style={selectedStyle(index, 'x')}
              />
            ) : null}
          </div>
        ))}
      </div>
      <div className='menu'>
        <button
          className='rule'
          onClick={() => setShowRuleWindow(true)}>
          Rules
        </button>
        <button className='reset' onClick={resetGame}>
          Reset Game
        </button>
        <button
          className='enableAI'
          onClick={() => {
            setEnableAI(!enableAI)
            resetGame()
          }}>
          AI {enableAI ? 'On' : 'Off'}
        </button>
        <button
          className='AIFirst'
          onClick={() => {
            setAiFirst(!aiFirst)
            resetGame()
          }}>
          AI {aiFirst ? 'First' : 'Second'}
        </button>
      </div>
      <div className='result'>{result}</div>
      <div className='author-display'>
        By <a href='https://github.com/decycle'>Decycle</a>{' '}
        - 2023
      </div>
      <RuleWindow
        show={showRuleWindow}
        close={() => setShowRuleWindow(false)}
      />
    </div>
  )
}

const RuleWindow = ({ show, close }) => {
  return (
    <div
      className='rule-window'
      style={{
        display: show ? 'block' : 'none',
      }}
      onClick={close}>
      <div
        className='rule-window-content'
        onClick={(e) => e.stopPropagation()}>
        <div className='rule-window-header'>
          <b>Rules</b>
        </div>
        <main className='rule-window-body'>
          <p>
            Chorus lapilli is an engaging game 🎲 similar to
            tic-tac-toe. You play on a 3x3 board, aiming to
            get three in a row.
          </p>
          <p>
            But there's a twist! After placing your first
            three pieces, you can only move them to a nearby
            empty spot. If you have a piece in the center,
            you must either win 🏆 (by connecting three in a
            row) or move it away on your turn. Enjoy 😊
          </p>
          <p>
            ps. Also the AI is borderline unbeatable😈, so
            good luck 🤞
          </p>
        </main>
        <div className='rule-window-footer'>
          <button className='close' onClick={close}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
