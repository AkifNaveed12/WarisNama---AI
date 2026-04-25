import React, { useState } from 'react'
import { FaMicrophone, FaMicrophoneSlash } from 'react-icons/fa'

const VoiceButton = ({ onTranscript, language = 'ur-PK' }) => {
  const [listening, setListening] = useState(false)
  const [recognition, setRecognition] = useState(null)

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.')
      return
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognitionInstance = new SpeechRecognition()
    recognitionInstance.continuous = false
    recognitionInstance.interimResults = false
    recognitionInstance.lang = language

    recognitionInstance.onstart = () => {
      setListening(true)
    }

    recognitionInstance.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      onTranscript(transcript)
      setListening(false)
    }

    recognitionInstance.onerror = (event) => {
      console.error('Speech recognition error', event.error)
      setListening(false)
    }

    recognitionInstance.onend = () => {
      setListening(false)
    }

    recognitionInstance.start()
    setRecognition(recognitionInstance)
  }

  const stopListening = () => {
    if (recognition) {
      recognition.stop()
      setListening(false)
    }
  }

  return (
    <button
      type="button"
      onClick={listening ? stopListening : startListening}
      className={`p-2 rounded-full ${
        listening ? 'bg-red-500 animate-pulse' : 'bg-gray-200 hover:bg-gray-300'
      }`}
      title={listening ? 'Stop listening' : 'Start voice input'}
    >
      {listening ? <FaMicrophoneSlash className="text-white" /> : <FaMicrophone className="text-gray-700" />}
    </button>
  )
}

export default VoiceButton