targetScope = 'subscription'

// The main bicep module to provision Azure resources.
// For a more complete walkthrough to understand how this file works with azd,
// see https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/make-azd-compatible?pivots=azd-create

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

// Optional parameters to override the default azd resource naming conventions.
// Add the following to main.parameters.json to provide values:
// "resourceGroupName": {
//      "value": "myGroupName"
// }
param resourceGroupName string = ''

// openai resouce region
@description('Region for the OpenAI resource')
@allowed(['eastus','eastus2','northcentralus','swedencentral','westus'])
param openaiRegion string = 'eastus'

param embeddingModel string = 'text-embedding-3-large'

// AI Search region
@description('Region for the AI Search resource')
@allowed(['eastus','eastus2','northcentralus','swedencentral','westus'])
param searchRegion string = 'eastus'

var abbrs = loadJsonContent('./abbreviations.json')

// tags that should be applied to all resources.
var tags = {
  // Tag all resources with the environment name.
  'azd-env-name': environmentName
}

// Generate a unique token to be used in naming resources.
// Remove linter suppression after using.
#disable-next-line no-unused-vars
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

// Name of the service defined in azure.yaml
// A tag named azd-service-name with this value should be applied to the service host resource, such as:
//   Microsoft.Web/sites for appservice, function
// Example usage:
//   tags: union(tags, { 'azd-service-name': apiServiceName })
#disable-next-line no-unused-vars
var apiServiceName = 'python-api'

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// Add resources to be provisioned below.
// A full example that leverages azd bicep modules can be seen in the todo-python-mongo template:
// https://github.com/Azure-Samples/todo-python-mongo/tree/main/infra

module storage 'core/storage/storage-account.bicep' = {
  name: 'stroage'
  scope: rg
  params: {
    name: '${abbrs.storageStorageAccounts}${resourceToken}'
    location: location
    tags: tags
    containers: [
      {name: 'docs'}
    ]
    isHnsEnabled: true
  }
}

// AI Search
module search 'core/search/search-services.bicep' = {
  name: 'search'
  scope: rg
  params: {
    name: '${abbrs.searchSearchServices}${resourceToken}'
    location: searchRegion
    tags: tags
    sku: {
      name: 'basic'
    }
  }
}

// Azure OpenAI
module openai 'core/ai/cognitiveservices.bicep' = {
  name: 'openai'
  scope: rg
  params: {
    name: 'aoai${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: openaiRegion
    tags: tags
    sku: {
      name: 'S0'
    }
    deployments: [
      {
        name: 'gpt4o'
        model: {
          format: 'OpenAI'
          name: 'gpt-4o'
          version: '2024-08-06'
        }
        sku: {
          name: 'Standard'
          capacity: 42
        }
      }
      {
        name: 'embedding'
        model: {
          format: 'OpenAI'
          name: embeddingModel
        }
      }
    ]
  }
}

// AI Studio Deployment
// Dependent resources for the Azure Machine Learning workspace

var aiHubFriendlyName = 'aihub'

@description('Description of your Azure AI resource dispayed in AI studio')
param aiHubDescription string = 'This is an example AI resource for use in Azure AI Studio.'

module aiDependencies 'core/ai/dependencies-resources.bicep' = {
  name: 'dependencies-${aiHubFriendlyName}-${resourceToken}-deployment'
  scope: rg
  params: {
    location: location
    storageName: 'st${aiHubFriendlyName}${resourceToken}'
    keyvaultName: 'kv-${aiHubFriendlyName}-${resourceToken}'
    applicationInsightsName: 'appi-${aiHubFriendlyName}-${resourceToken}'
    containerRegistryName: 'cr${aiHubFriendlyName}${resourceToken}'
    // aiServicesName: 'ais${aiHubFriendlyName}${resourceToken}'
    tags: tags
  }
}

module aiHub 'core/ai/ai-hub.bicep' = {
  name: 'ai-${aiHubFriendlyName}-${resourceToken}-deployment'
  scope: rg
  params: {
    // workspace organization
    aiHubName: 'aih-${aiHubFriendlyName}-${resourceToken}'
    aiHubFriendlyName: aiHubFriendlyName
    aiHubDescription: aiHubDescription
    location: location
    tags: tags

    // dependent resources
    aiServicesId: openai.outputs.id
    aiServicesTarget: openai.outputs.endpoint
    aiSearchId: search.outputs.id
    aiSearchName: search.outputs.name
    aiSearchTarget: search.outputs.endpoint
    applicationInsightsId: aiDependencies.outputs.applicationInsightsId
    containerRegistryId: aiDependencies.outputs.containerRegistryId
    keyVaultId: aiDependencies.outputs.keyvaultId
    storageAccountId: aiDependencies.outputs.storageId
  }
}

module aiProject 'core/ai/project.bicep' = {
  name: 'ai-project'
  scope: rg
  params: {
    location: location
    displayName: 'AI Project'
    hubName: 'aih-${aiHubFriendlyName}-${resourceToken}'
    keyVaultName: 'kv-${aiHubFriendlyName}-${resourceToken}'
    skuName: 'Basic'
    skuTier: 'Basic'
    name: 'ai-project'
    tags: tags
  }
}

// AI Services
module aiservices 'core/ai/cognitiveservices-preview.bicep' = {
  name: 'aiservices'
  scope: rg
  params: {
    name: 'aiservices${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: searchRegion
    kind: 'CognitiveServices'
    tags: tags
    sku: {
      name: 'S0'
    }
  }
}

// Role Assignment for AI Search. "Search Index Data Contributor" role to the AI Search service principal.
// module aisearch_role 'core/security/role.bicep' = {
//   name: 'aisearch-role-assignment'
//   scope: rg
//   params: {
//     principalId: search.outputs.principalId
//     roleDefinitionId: '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
//   }
// }

// Add outputs from the deployment here, if needed.
//
// This allows the outputs to be referenced by other bicep deployments in the deployment pipeline,
// or by the local machine as a way to reference created resources in Azure for local development.
// Secrets should not be added here.
//
// Outputs are automatically saved in the local azd environment .env file.
// To see these outputs, run `azd env get-values`,  or `azd env get-values --output json` for json output.
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId

// Storage Outputs
output AZURE_STORAGE_ACCOUNT_NAME string = storage.outputs.name
output AZURE_STORAGE_CONTAINER_NAME string = storage.outputs.containerName
output AZURE_STORAGE_ACCOUNT_KEY string = storage.outputs.storageAccountKey
output AZURE_STORAGE_CONNECTION_STRING string = storage.outputs.storageAccountConnectionString

// AI Search Outputs
output AZURE_SEARCH_ENDPOINT string = search.outputs.endpoint
output AZURE_SEARCH_PRINCIPAL_ID string = search.outputs.principalId
output AZURE_SEARCH_KEY string = search.outputs.primaryKey

// OpenAI Outputs
output AZURE_OPENAI_ENDPOINT string = openai.outputs.endpoint
output AZURE_OPENAI_KEY string = openai.outputs.accountKey
output AZURE_OPENAI_EMBEDDING_MODEL string = embeddingModel

// AI Services Ouputs
output AZURE_AI_SERVICES_ENDPOINT string = aiservices.outputs.endpoint
output AZURE_AI_SERVICES_KEY string = aiservices.outputs.accountKey
