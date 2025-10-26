'use client'

import { 
  DocumentTextIcon, 
  QuestionMarkCircleIcon,
  StarIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid'

interface SourcesPanelProps {
  sources?: {
    knowledge_base_hits: Array<{
      id: string
      content: string
      filename: string
      similarity_score: number
    }>
    qa_hits: Array<{
      id: string
      question: string
      answer: string
      similarity_score: number
    }>
  }
}

export function SourcesPanel({ sources }: SourcesPanelProps) {
  const renderSimilarityScore = (score: number) => {
    const percentage = Math.round(score * 100)
    const stars = Math.round(score * 5)
    
    return (
      <div className="flex items-center space-x-2">
        <div className="flex">
          {[1, 2, 3, 4, 5].map((star) => (
            star <= stars ? (
              <StarIconSolid key={star} className="w-3 h-3 text-yellow-400" />
            ) : (
              <StarIcon key={star} className="w-3 h-3 text-gray-300" />
            )
          ))}
        </div>
        <span className="text-xs text-gray-500">{percentage}%</span>
      </div>
    )
  }

  const truncateText = (text: string, maxLength: number = 150) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <InformationCircleIcon className="w-5 h-5 mr-2" />
          Sources
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Information used to generate the response
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {!sources ? (
          <div className="text-center py-8">
            <InformationCircleIcon className="mx-auto h-8 w-8 text-gray-400" />
            <p className="mt-2 text-sm text-gray-500">
              Send a message to see sources
            </p>
          </div>
        ) : (
          <>
            {/* Knowledge Base Hits */}
            {sources.knowledge_base_hits && sources.knowledge_base_hits.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                  <DocumentTextIcon className="w-4 h-4 mr-2" />
                  Knowledge Base ({sources.knowledge_base_hits.length})
                </h4>
                <div className="space-y-3">
                  {sources.knowledge_base_hits.map((hit, index) => (
                    <div key={hit.id} className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                      <div className="flex items-start justify-between mb-2">
                        <span className="text-xs font-medium text-blue-800">
                          {hit.filename}
                        </span>
                        {renderSimilarityScore(hit.similarity_score)}
                      </div>
                      <p className="text-sm text-gray-700">
                        {truncateText(hit.content)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Q&A Hits */}
            {sources.qa_hits && sources.qa_hits.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
                  <QuestionMarkCircleIcon className="w-4 h-4 mr-2" />
                  Q&A Pairs ({sources.qa_hits.length})
                </h4>
                <div className="space-y-3">
                  {sources.qa_hits.map((hit, index) => (
                    <div key={hit.id} className="bg-green-50 rounded-lg p-3 border border-green-200">
                      <div className="flex items-start justify-between mb-2">
                        <span className="text-xs font-medium text-green-800">
                          Q&A Match
                        </span>
                        {renderSimilarityScore(hit.similarity_score)}
                      </div>
                      <div className="space-y-2">
                        <div>
                          <p className="text-xs font-medium text-gray-600">Question:</p>
                          <p className="text-sm text-gray-700">
                            {truncateText(hit.question, 100)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs font-medium text-gray-600">Answer:</p>
                          <p className="text-sm text-gray-700">
                            {truncateText(hit.answer, 100)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* No Sources */}
            {(!sources.knowledge_base_hits || sources.knowledge_base_hits.length === 0) &&
             (!sources.qa_hits || sources.qa_hits.length === 0) && (
              <div className="text-center py-8">
                <InformationCircleIcon className="mx-auto h-8 w-8 text-gray-400" />
                <p className="mt-2 text-sm text-gray-500">
                  No relevant sources found
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  The AI generated a response without specific source matches
                </p>
              </div>
            )}
          </>
        )}
      </div>

      {/* Legend */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <h5 className="text-xs font-medium text-gray-700 mb-2">Similarity Score</h5>
        <div className="space-y-1 text-xs text-gray-600">
          <div className="flex items-center space-x-2">
            <div className="flex">
              {[1, 2, 3, 4, 5].map((star) => (
                <StarIconSolid key={star} className="w-2.5 h-2.5 text-yellow-400" />
              ))}
            </div>
            <span>Excellent match (80-100%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex">
              {[1, 2, 3, 4].map((star) => (
                <StarIconSolid key={star} className="w-2.5 h-2.5 text-yellow-400" />
              ))}
              <StarIcon className="w-2.5 h-2.5 text-gray-300" />
            </div>
            <span>Good match (60-79%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex">
              {[1, 2, 3].map((star) => (
                <StarIconSolid key={star} className="w-2.5 h-2.5 text-yellow-400" />
              ))}
              {[4, 5].map((star) => (
                <StarIcon key={star} className="w-2.5 h-2.5 text-gray-300" />
              ))}
            </div>
            <span>Fair match (40-59%)</span>
          </div>
        </div>
      </div>
    </div>
  )
}
